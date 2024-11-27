import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

# Function to display the Gantt chart
def show_gantt_chart(schedule):
    fig, ax = plt.subplots(figsize=(8, 4))

    for machine, tasks in schedule.items():
        for task in tasks:
            job, start, end = task
            ax.barh(machine, end - start, left=start, edgecolor='black', label=f'Job {job}')
            ax.text(start + (end - start) / 2, machine, f"Job {job}", va='center', ha='center', color='white')

    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_yticks(list(schedule.keys()))
    ax.set_yticklabels([f"Machine {m}" for m in schedule.keys()])
    ax.set_title('Job Scheduling Gantt Chart')
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame_gantt)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Genetic Algorithm for Job Scheduling
def genetic_algorithm(jobs, machines, population_size=50, generations=100, mutation_rate=0.1):
    def initialize_population():
        population = []
        for _ in range(population_size):
            individual = random.sample(jobs, len(jobs))
            population.append(individual)
        return population

    def fitness(schedule):
        machine_times = {m: 0 for m in machines}
        for job in schedule:
            job_id, operation, machine, proc_time = job
            machine_times[machine] += proc_time
        return max(machine_times.values())

    def crossover(parent1, parent2):
        point = random.randint(0, len(jobs) - 1)
        child = parent1[:point] + [job for job in parent2 if job not in parent1[:point]]
        return child

    def mutate(individual):
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]

    def create_schedule(individual):
        machine_schedule = {m: [] for m in machines}
        machine_end_times = {m: 0 for m in machines}
        for job in individual:
            job_id, operation, machine, proc_time = job
            start_time = machine_end_times[machine]
            end_time = start_time + proc_time
            machine_schedule[machine].append((job_id, start_time, end_time))
            machine_end_times[machine] = end_time
        return machine_schedule

    population = initialize_population()
    for _ in range(generations):
        population = sorted(population, key=lambda ind: fitness(ind))[:population_size]
        next_generation = []
        for i in range(0, len(population), 2):
            if i + 1 < len(population):
                parent1, parent2 = population[i], population[i + 1]
                child1 = crossover(parent1, parent2)
                child2 = crossover(parent2, parent1)
                mutate(child1)
                mutate(child2)
                next_generation.extend([child1, child2])
        population.extend(next_generation)

    best_individual = min(population, key=lambda ind: fitness(ind))
    return create_schedule(best_individual)

# Function to run the backtracking approach
def backtracking_algorithm(jobs, machines):
    def is_safe(machine_schedule, machine, start, end):
        for job in machine_schedule[machine]:
            if not (end <= job[1] or start >= job[2]):
                return False
        return True

    def backtrack(idx, machine_schedule):
        if idx == len(jobs):
            return True, machine_schedule
        job_id, operation, machine, proc_time = jobs[idx]
        for start in range(0, 100):  # Search a reasonable time window
            end = start + proc_time
            if is_safe(machine_schedule, machine, start, end):
                machine_schedule[machine].append((job_id, start, end))
                success, result = backtrack(idx + 1, machine_schedule)
                if success:
                    return success, result
                machine_schedule[machine].pop()
        return False, None

    machine_schedule = {m: [] for m in machines}
    success, result = backtrack(0, machine_schedule)
    if success:
        return result
    else:
        messagebox.showerror("Backtracking Error", "No feasible schedule found!")
        return None

# Function to handle "Run Algorithm" button
def run_algorithm():
    try:
        jobs = []
        for child in tree_jobs.get_children():
            job_data = tree_jobs.item(child)['values']
            jobs.append((int(job_data[0]), int(job_data[1]), int(job_data[2]), int(job_data[3])))

        machines = []
        for child in tree_machines.get_children():
            machine_data = tree_machines.item(child)['values']
            machines.append(int(machine_data[0]))

        if not jobs or not machines:
            messagebox.showwarning("Input Error", "Please enter both jobs and machines!")
            return

        use_genetic = algo_choice.get() == "Genetic Algorithm"
        if use_genetic:
            schedule = genetic_algorithm(jobs, machines)
        else:
            schedule = backtracking_algorithm(jobs, machines)

        if schedule:
            show_gantt_chart(schedule)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Job Scheduling Solver")
root.geometry("1100x700")

# Frames for different sections
frame_inputs = ttk.LabelFrame(root, text="Input Section", padding="10")
frame_inputs.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=5, expand=True)

frame_gantt = ttk.LabelFrame(root, text="Gantt Chart", padding="10")
frame_gantt.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=5, expand=True)

# Section: Jobs Input
label_jobs = ttk.Label(frame_inputs, text="Jobs")
label_jobs.grid(row=0, column=0, sticky=tk.W, pady=5)

tree_jobs = ttk.Treeview(frame_inputs, columns=("Job ID", "Operation", "Machine", "Processing Time"), show="headings")
tree_jobs.grid(row=1, column=0, columnspan=5, sticky=tk.W + tk.E, pady=5)
tree_jobs.heading("Job ID", text="Job ID")
tree_jobs.heading("Operation", text="Operation")
tree_jobs.heading("Machine", text="Machine")
tree_jobs.heading("Processing Time", text="Processing Time")

def add_job():
    try:
        job_id = int(entry_job_id.get())
        operation = int(entry_operation.get())
        machine = int(entry_machine.get())
        proc_time = int(entry_processing_time.get())
        tree_jobs.insert("", tk.END, values=(job_id, operation, machine, proc_time))
        entry_job_id.delete(0, tk.END)
        entry_operation.delete(0, tk.END)
        entry_machine.delete(0, tk.END)
        entry_processing_time.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for job details!")

frame_job_input = ttk.Frame(frame_inputs)
frame_job_input.grid(row=2, column=0, columnspan=5, pady=5)

ttk.Label(frame_job_input, text="Job ID").grid(row=0, column=0, padx=5)
entry_job_id = ttk.Entry(frame_job_input, width=5)
entry_job_id.grid(row=0, column=1, padx=5)

ttk.Label(frame_job_input, text="Operation").grid(row=0, column=2, padx=5)
entry_operation = ttk.Entry(frame_job_input, width=5)
entry_operation.grid(row=0, column=3, padx=5)

ttk.Label(frame_job_input, text="Machine").grid(row=0, column=4, padx=5)
entry_machine = ttk.Entry(frame_job_input, width=5)
entry_machine.grid(row=0, column=5, padx=5)

ttk.Label(frame_job_input, text="Processing Time").grid(row=0, column=6, padx=5)
entry_processing_time = ttk.Entry(frame_job_input, width=10)
entry_processing_time.grid(row=0, column=7, padx=5)

btn_add_job = ttk.Button(frame_job_input, text="Add Job", command=add_job)
btn_add_job.grid(row=0, column=8, padx=5)

# Section: Machines Input
label_machines = ttk.Label(frame_inputs, text="Machines")
label_machines.grid(row=3, column=0, sticky=tk.W, pady=5)

tree_machines = ttk.Treeview(frame_inputs, columns=("Machine ID",), show="headings")
tree_machines.grid(row=4, column=0, columnspan=5, sticky=tk.W + tk.E, pady=5)
tree_machines.heading("Machine ID", text="Machine ID")

def add_machine():
    try:
        machine_id = int(entry_machine_id.get())
        tree_machines.insert("", tk.END, values=(machine_id,))
        entry_machine_id.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Invalid input for machine ID!")

frame_machine_input = ttk.Frame(frame_inputs)
frame_machine_input.grid(row=5, column=0, columnspan=5, pady=5)

ttk.Label(frame_machine_input, text="Machine ID").grid(row=0, column=0, padx=5)
entry_machine_id = ttk.Entry(frame_machine_input, width=10)
entry_machine_id.grid(row=0, column=1, padx=5)

btn_add_machine = ttk.Button(frame_machine_input, text="Add Machine", command=add_machine)
btn_add_machine.grid(row=0, column=2, padx=5)

# Algorithm selection
algo_choice = tk.StringVar(value="Genetic Algorithm")
ttk.Radiobutton(frame_inputs, text="Genetic Algorithm", variable=algo_choice, value="Genetic Algorithm").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Radiobutton(frame_inputs, text="Backtracking", variable=algo_choice, value="Backtracking").grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

# Run Algorithm Button
btn_run = ttk.Button(frame_inputs, text="Run Algorithm", command=run_algorithm)
btn_run.grid(row=7, column=0, columnspan=5, pady=10)

# Main loop
root.mainloop()
