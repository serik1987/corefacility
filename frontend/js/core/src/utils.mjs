export function wait(duration){
	return new Promise((resolve, reject) => {
		if (duration < 0){
			reject(new RangeError("In wait() function the value of duration must be non-negative"));
		}
		setTimeout(resolve, duration);
	});
}
