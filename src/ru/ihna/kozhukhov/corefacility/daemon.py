import sys
import os
import time
import signal
import systemd.daemon
import psutil


class CorefacilityDaemon:
	"""
	The corefacility daemon is an intermediate between the systemd on the one side and 'corefacility autoadmin' and
	'corefacility health_check' on the other side.

	When the server boots the systemd invokes the CorefacilityDaemon utility. The main job of the CorefacilityDaemon
	is to invoke the 'corefacility autoadmin' and the 'corefacility health_check' that are reffered to as 
	child processes.

	When the CorefacilityDaemon receives the INT, TERM or QUIT signals they are propagated to the child processes.
	The HUP signal causes restart of both child processes. Also, the child processes will be restarted when they eat
	too much memory (probably, due to the memory leakage).
	"""

	TERMINATION_SIGNALS = {
		signal.SIGINT: "INT",
		signal.SIGTERM: "TERM",
		signal.SIGQUIT: "QUIT",
	}

	CHILD_COMMANDS = {
		'autoadmin': ['corefacility', 'autoadmin'],
		'healthcheck': ['corefacility', 'health_check'],
	}

	LOOP_ITERATION_TIME = 1  # seconds

	MAX_SIZE = 300 * 1024 * 1024  # Maximum size for the child processes (both children shall not exceed this size)

	is_interrupted = False
	child_pids = None

	def __init__(self):
		"""
		Initializes the daemon
		"""
		self.is_interrupted = False
		self.child_pids = dict()

	def terminate(self, signal_number, traceback):
		"""
		Destroys the daemon parent process.
		The method invokes automatically when the parent process receives the termination signal.

		@param signal_number 		number of the POSIX signal that initiates the process termination
		@param traceback 			useless
		"""
		print("The daemon has received the {0} signal. Finishing the job..."
			.format(self.TERMINATION_SIGNALS[signal_number]))
		self.is_interrupted = True
		for child_pid in self.child_pids.values():
			os.kill(child_pid, signal.SIGTERM)

	def reload_configuration(self, signal_number, traceback):
		print("The daemon will reload its configuration. All child processes will be stopped and started again.")
		child_pids = list(self.child_pids.values())
		for child_pid in child_pids:
			os.kill(child_pid, signal.SIGTERM)

	def start_child(self, child_name, child_command):
		"""
		Starts one of the child processes: autoadmin, health_check etc.
		The new child process will first be fork()'ed and them will be substituted by the running command.

		@param child_name 		Some string that reflects short name of the child process
		@param child_command 	Name of the POSIX command and POSIX command arguments that will be executed during the
								process
		"""
		child_pid = os.fork()
		if child_pid == 0:  # We deal with the child process
			os.execvp(child_command[0], child_command)
		else:  # We deal with the parent process
			self.child_pids[child_name] = child_pid

	def run(self):
		"""
		Toggles the daemon into the infinite loop that reflects the normal daemon job.
		"""
		if os.getuid() != 0:
			print("The corefacility daemon must be run under the root", file=sys.stderr)
			sys.exit(1)

		for signal_number in self.TERMINATION_SIGNALS.keys():
			signal.signal(signal_number, self.terminate)
		signal.signal(signal.SIGHUP, self.reload_configuration)

		for child_name, child_command in self.CHILD_COMMANDS.items():
			self.start_child(child_name, child_command)

		systemd.daemon.notify("READY=1")

		while True:
			try:
				time.sleep(self.LOOP_ITERATION_TIME)
				for child_name, child_pid in self.child_pids.items():
					try:
						child_process = psutil.Process(child_pid)
						if child_process.status() in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
							continue
						child_memory = child_process.memory_info().vms
						if child_memory > self.MAX_SIZE:
							print("The process '%s' with PID=%d allocated too higher than %d bytes of virtual memory " +
								"and will be restarted" % (child_name, child_pid, self.MAX_SIZE))
							os.kill(child_pid, signal.SIGTERM)
					except psutil.NoSuchProcess:
						pass
				child_pid, exit_status = os.waitpid(-1, os.WNOHANG)  # -1 means 'all processes'
				# child_pid != 0 means no child process has been terminated
				if child_pid != 0:
					print("The process with PID=%d has been terminated with exit code %d" % (child_pid, exit_status))
				if child_pid != 0 and not self.is_interrupted:
					process_name = list(self.child_pids.keys())[list(self.child_pids.values()).index(child_pid)]
					print("Reloading the process '%s'" % process_name)
					child_command = self.CHILD_COMMANDS[process_name]
					self.start_child(process_name, child_command)
			except ChildProcessError:  # will be thrown by the os.waitpid if no child processes were serviced
				break

		print("The daemon has finished the job.")


def main():
	"""
	An auxiliary function that launches the daemon program.
	"""
	daemon = CorefacilityDaemon()
	daemon.run()
