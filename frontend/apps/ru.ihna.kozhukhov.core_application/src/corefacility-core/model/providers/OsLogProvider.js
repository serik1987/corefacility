import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';


/**
 * 	The class is responsible for interaction between the OsLog entity and and Web server.
 */
export default class OsLogProvider extends HttpRequestProvider{

	/**
	 * 	Creates new instance of the OsLogProvider
	 * 
	 * 	@param {function} entityClass 	The entity class to which the OsLogProvider shall be attached
	 */
	constructor(entityClass){
		super("os-logs", entityClass, true);
	}

	/** Transforms list of entity response containing in the response body to the list of entities
     *  @param {list[object]} list of objects containing in the output response
     *  @return {list[Entity]} list of Entities found
     */
    _resultToListMapper(responseData){
    	OsLogProvider.logFiles = responseData.log_files;
    	OsLogProvider.hostList = responseData.host_list;
    	return super._resultToListMapper(responseData.log_data);
    }

}

OsLogProvider.logFiles = [];
OsLogProvider.hostList = [];