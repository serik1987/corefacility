import client from './HttpClient';


/** Represents module icon to be displayed in the authorization form etc.
 */
export default class ModuleWidget{

	/** Creates new module
	 */
	constructor(uuid, alias, name, htmlCode){
		this._uuid = uuid;
		this._alias = alias;
		this._name = name;
		this._htmlCode = htmlCode;
	}

	/** Module UUID */
	get uuid(){
		return this._uuid;
	}

	/** Module alias */
	get alias(){
		return this._alias;
	}

	/** Module name */
	get name(){
		return this._name;
	}

	get htmlCode(){
		return this._htmlCode;
	}

	/** Transforms the module widget to string */
	toString(){
		return `ModuleWidget(uuid=${this.uuid}, alias=${this.alias}, name=${this.name}, htmlCode=${this.htmlCode})`;
	}

	/** Downloads all widgets attached to a given Web server. Only widgets related to enabled modules will be
	 * 	considered.
	 * 	
	 * 	@static
	 * 	@generator
	 * 	@async
	 * 	@param {string} parentModuleUuid UUID of the parent module
	 * 	@param {entryPointAlias} entryPointAlias the entry point alias
	 * 	@return
	 */
	static async *find(parentModuleUuid, entryPointAlias){
		let result;

		if (this.__pending){
			return;
		}

		this.initializeResultCache(false);
		let argFootprint = `${parentModuleUuid}:${entryPointAlias}`;
		if (argFootprint in this.__resultCache){
			result = this.__resultCache[argFootprint];
		} else {
			try{
				this.__pending = true;
				let url = `/api/${window.SETTINGS.client_version}/widgets/${parentModuleUuid}/${entryPointAlias}/`;
				result = await client.get(url);
				this.__resultCache[argFootprint] = result;
			} catch (error) {
				throw error;
			} finally{
				this.__pending = false;
			}
		}

		for (let widgetInfo of result){
			yield new ModuleWidget(widgetInfo.uuid, widgetInfo.alias, widgetInfo.name, widgetInfo.html_code);
		}
	}

	/** Initializes the result cache
	 * 	@param {boolean} force clear previous cache
	 */
	static initializeResultCache(force=true){
		if (force || this.__resultCache === undefined){
			this.__resultCache = [];
		}
	}

}