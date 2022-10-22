import i18next from "i18next";


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
