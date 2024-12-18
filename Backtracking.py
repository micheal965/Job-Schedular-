import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import random


class Job:
    def __init__(self, job_id, processing_time, required_machines):
        self.job_id = job_id
        self.processing_time = processing_time
        self.required_machines = required_machines


class Machine:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity


class JobScheduler:
    def __init__(self, jobs, dependencies, machines):
        self.jobs = {job.job_id: job for job in jobs}
        self.dependencies = dependencies
        self.machines = {machine.name: machine for machine in machines}
        self.schedule = {}
        self.graph = defaultdict(list)
        self.in_degree = {job_id: 0 for job_id in self.jobs}
        self.result = []
        self.start_times = {}
        self._build_graph()

    def _build_graph(self):
        for u, v in self.dependencies:
            self.graph[u].append(v)
            self.in_degree[v] += 1

    def topological_sort(self):
        topo_order = []
        queue = deque([job_id for job_id in self.jobs if self.in_degree[job_id] == 0])
        while queue:
            u = queue.popleft()
            topo_order.append(u)
            for v in self.graph[u]:
                self.in_degree[v] -= 1
                if self.in_degree[v] == 0:
                    queue.append(v)
        return topo_order if len(topo_order) == len(self.jobs) else []

    def schedule_jobs(self):
        topo_order = self.topological_sort()
        if not topo_order:
            print("No valid topological order (possible circular dependency).")
            return []

        machine_usage = {machine: 0 for machine in self.machines}
        for job_id in topo_order:
            job = self.jobs[job_id]
            start_time = 0
            for machine in job.required_machines:
                start_time = max(start_time, machine_usage[machine])
            for machine in job.required_machines:
                machine_usage[machine] = start_time + job.processing_time
            self.schedule[job_id] = (start_time, job.required_machines)
            self.start_times[job_id] = start_time

        return self.schedule

    def draw_gantt_chart(self):
        if not self.schedule:
            print("No schedule to draw.")
            return

        fig, ax = plt.subplots()
        machine_names = list(self.machines.keys())
        machine_indices = {name: idx for idx, name in enumerate(machine_names)}
        job_colors = {}

        for job_id in self.schedule:
            if job_id not in job_colors:
                job_colors[job_id] = (random.random(), random.random(), random.random())
            start_time, machines = self.schedule[job_id]
            for machine in machines:
                machine_idx = machine_indices[machine]
                ax.broken_barh([(start_time, self.jobs[job_id].processing_time)],
                               (10 * machine_idx, 9),
                               facecolors=job_colors[job_id])
                ax.text(start_time + self.jobs[job_id].processing_time / 2,
                        10 * machine_idx + 4.5,
                        f"Job {job_id}",
                        ha='center', va='center', color='white')

        ax.set_yticks([10 * idx + 4.5 for idx in range(len(machine_names))])
        ax.set_yticklabels(machine_names)
        ax.set_xlabel('Time')
        ax.set_ylabel('Machines')
        ax.set_title('Gantt Chart')
        plt.show()


class JobSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scheduler")

        self.jobs = []
        self.dependencies = []
        self.machines = []

        self.setup_ui()

    def setup_ui(self):
        self.job_frame = tk.LabelFrame(self.root, text="Add Jobs")
        self.job_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.job_frame, text="Job ID:").grid(row=0, column=0)
        self.job_id_entry = tk.Entry(self.job_frame, width=10)
        self.job_id_entry.grid(row=0, column=1)

        tk.Label(self.job_frame, text="Processing Time:").grid(row=0, column=2)
        self.job_time_entry = tk.Entry(self.job_frame, width=10)
        self.job_time_entry.grid(row=0, column=3)

        tk.Label(self.job_frame, text="Required Machines (comma-separated):").grid(row=0, column=4)
        self.job_res_entry = tk.Entry(self.job_frame, width=20)
        self.job_res_entry.grid(row=0, column=5)

        self.add_job_button = tk.Button(self.job_frame, text="Add Job", command=self.add_job_with_dependencies)
        self.add_job_button.grid(row=0, column=6)

        self.res_frame = tk.LabelFrame(self.root, text="Add Machines")
        self.res_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.res_frame, text="Machine Name:").grid(row=0, column=0)
        self.res_name_entry = tk.Entry(self.res_frame, width=10)
        self.res_name_entry.grid(row=0, column=1)

        tk.Label(self.res_frame, text="Capacity (Total Time Available):").grid(row=0, column=2)
        self.res_capacity_entry = tk.Entry(self.res_frame, width=10)
        self.res_capacity_entry.grid(row=0, column=3)

        self.add_res_button = tk.Button(self.res_frame, text="Add Machine", command=self.add_machine)
        self.add_res_button.grid(row=0, column=4)

        self.gantt_button = tk.Button(self.root, text="Show Gantt Chart", command=self.show_gantt_chart)
        self.gantt_button.pack(pady=10)

    def add_job_with_dependencies(self):
        job_id = self.job_id_entry.get()
        time = self.job_time_entry.get()
        required_machines = self.job_res_entry.get().split(",")

        if job_id and time.isdigit() and required_machines:
            job_id = int(job_id)
            processing_time = int(time)
            self.jobs.append(Job(job_id, processing_time, required_machines))
            messagebox.showinfo("Success", f"Job {job_id} added!")

            dependencies = simpledialog.askstring(
                "Add Dependencies",
                f"Enter job IDs that Job {job_id} depends on, separated by commas (leave empty if none):"
            )
            if dependencies:
                for dep in dependencies.split(","):
                    if dep.strip().isdigit():
                        self.dependencies.append((int(dep.strip()), job_id))

            self.job_id_entry.delete(0, tk.END)
            self.job_time_entry.delete(0, tk.END)
            self.job_res_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Invalid Job ID, Processing Time, or Machines.")

    def add_machine(self):
        machine_name = self.res_name_entry.get()
        capacity = self.res_capacity_entry.get()
        if machine_name and capacity.isdigit():
            self.machines.append(Machine(machine_name, int(capacity)))
            messagebox.showinfo("Success", f"Machine {machine_name} added!")
            self.res_name_entry.delete(0, tk.END)
            self.res_capacity_entry.delete(0, tk.END)

    def show_gantt_chart(self):
        scheduler = JobScheduler(self.jobs, self.dependencies, self.machines)
        result = scheduler.schedule_jobs()
        if result:
            scheduler.draw_gantt_chart()
        else:
            messagebox.showinfo("No Schedule", "No valid schedules found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = JobSchedulerGUI(root)
    root.mainloop()

# Test

# Add Machines:
#
# Machine A with capacity 100.
# Machine B with capacity 100.
# Machine C with capacity 100.
# Add Jobs:
#
# Job 1: Processing time = 5, Required machine = A.
# Job 2: Processing time = 8, Required machine = B.
# Job 3: Processing time = 3, Required machine = C.
# Job 4: Processing time = 6, Required machines = A, B. Dependency = Job 1.
# Job 5: Processing time = 4, Required machines = B, C. Dependencies = Job 2, Job 3.


# Schedule Result:
#
# Job 1: Starts at time 0, using machine A.
# Job 2: Starts at time 0, using machine B.
# Job 3: Starts at time 0, using machine C.
# Job 4: Starts at time 8, using machines A and B (dependent on Job 1).
# Job 5: Starts at time 14, using machines B and C (dependent on Jobs 2 and 3).