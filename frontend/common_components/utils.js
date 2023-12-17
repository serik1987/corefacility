import i18next from "i18next";

const MEMORY_UNITS = {
	'Tb': 1024 * 1024 * 1024 * 1024,
	'Gb': 1024 * 1024 * 1024,
	'Mb': 1024 * 1024,
	'Kb': 1024,
	'B':  1,
}
const PRECISION = 2;


/** Waits for a given number of milliseconds.
 *  @async
 *  @param {number} duration number of milliseconds to wait
 *  @return {undefined}
 */
export function wait(duration){
	return new Promise((resolve, reject) => {
		if (duration < 0){
			reject(new RangeError("In wait() function the value of duration must be non-negative"));
		}
		setTimeout(resolve, duration);
	});
}

const id = (() => {
	let lastAddedId = 0;
	const map = new WeakMap();
	return object => {
		if (!map.has(object)){
			map.set(object, ++lastAddedId);
		}
		return map.get(object);
	}
})();

export {id};

/** Translates the message or returns the message itself
 *  if translation fails.
 *  @param {string} message the message to translate
 * 	@return {string} translated message
 */
export function translate(message){
	let translation = null;

	try{
		translation = i18next.t(message);
		if (translation === null || translation === undefined || translation === ''){
			translation = message;
		}
	} catch (e){
		translation = message;
	}

	return translation;
}

/**
 * 	Checks whether a given date is valid
 * 
 * 	@param {Date} date 		the date to check
 * 	@return {boolean} 		true if the date is valid, false otherwise
 */
export function isDateValid(date){
	return !isNaN(date.getTime());

}

/**
 *  Transforms the memory measure to human-readable format.
 * 	@param {Number} size 		Memory size in bytes
 * 	@return {String} 			A string like '4.2 Gb' or '3.8 Mb'
 */
export function humanReadableMemory(size){
	size = Math.round(size);
	for (let unit in MEMORY_UNITS){
		let unitValue = MEMORY_UNITS[unit];
		if (Math.abs(size) > unitValue){
			return `${(size / unitValue).toFixed(PRECISION)} ${translate(unit)}`;
		}
	}

	return '0';
}
