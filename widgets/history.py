from textual.app import ComposeResult
from textual.widgets import Label
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import VerticalScroll
import asyncio
from widgets.temp import Heater, TemperatureFan
from widgets.job import Job
from screens.print import PrintScreen

class KluiHistory(Widget):
    jobs = []
    selected_job = reactive(0)
    NUM_JOBS = 10

    def compose(self) -> ComposeResult:
        yield Label("Files", classes="title")
        yield VerticalScroll(id='files')

    async def update(self, data):
        # get only latest job for up to 10 files
        jobs = {}
        jobs_by_id = {}

        for job in data:
            if job['filename'] in jobs.keys():
                continue
            jobs[job['filename']] = job
            jobs_by_id[job['job_id']] = job
            if len(jobs.keys()) >= self.NUM_JOBS:
                break

        self.jobs = list(jobs.values())
        async def get_widget(job) -> Job:
            tmp = Job(
                job['job_id'] + ' ' + job['filename'],
                id='job_'+job['job_id'],
                classes="job",
            )

            await self.query_one('#files').mount(tmp)
            tmp.set_filename('[b]'+job['filename']+'[/]')
            print(job)
            tmp.set_meta(job['print_duration'], job['filament_used'], job['metadata']['filament_weight_total'])
            tmp.query_one('#status').label = job['status'].title()
            return self.query_one('#job_'+job['job_id'])


        results = await asyncio.gather(*map(get_widget, jobs.values()))
        self.query(Job).first().classes = 'job selected'

            

    def on_key(self, event):
        if event.key and event.key == "up":
            self.selected_job -= 1
            if self.selected_job < 0:
                self.selected_job = 0
            for i, ax in enumerate(self.query(Job)):
                if self.selected_job == i:
                    ax.classes = 'job selected'
                else:
                    ax.classes = 'job unselected'
                ax.refresh()
        elif event.key and event.key == "down":
            self.selected_job += 1
            if self.selected_job >= self.NUM_JOBS:
                self.selected_job = self.NUM_JOBS-1
            for i, ax in enumerate(self.query(Job)):
                if self.selected_job == i:
                    ax.classes = 'job selected'
                else:
                    ax.classes = 'job unselected'
                ax.refresh()
        elif event.key and event.key == "enter":
            # print('will print ', self.jobs[self.selected_job]['filename'])
            self.app.push_screen(PrintScreen(self.jobs[self.selected_job]))