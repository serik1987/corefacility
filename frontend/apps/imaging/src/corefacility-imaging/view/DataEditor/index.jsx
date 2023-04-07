import {translate as t} from 'corefacility-base/utils';
import SidebarEditor from 'corefacility-base/view/SidebarEditor';
import DataUploader from 'corefacility-base/shared-view/components/DataUploader';
import FunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import DataList from '../DataList';
import style from './style.module.css';


/**
 * 	Represents list of functional maps together with facilities for uploading and downloading a single map.
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param 	{Number} 	lookup 					ID of the map to open on the right side. undefined will not open any map
 * 												on the right side
 * 	@param 	{callback}	onItemAddOpen			This is an asynchronous method that opens
 * 												add entity box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 *  @param {callback} onItemChangeOpen          An asynchronous method that opens each time the user opens the modify
 *                                              entity box (either page or modal box). The promise always fulfills when
 *                                              the user close the box. The promise can be never rejected.
 * 
 *	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  You can manage loading state through reportListFetch(), reportFetchSuccess(itemList), reportFetchFailure(error)
 *  @param {Number} itemId                      ID of the item to open.
 *  @param {Entity} item                        The item currently selected by the user.
 * 	@param {string} uploadError 				An error occured during the file upload.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 *  @param {Number}   itemId                    ID of the opened item.
 *  @param {callback} onItemOpen                This method must be triggered when the user tries to open the item on
 *                                              the right pane.
 * 	@param {callback} onItemSelect				This method must be triggered when the user tries to change the item.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class DataEditor extends SidebarEditor{

	constructor(props){
		super(props);
		this.handleUploadError = this.handleUploadError.bind(this);

		this.state = {
			...this.state,
			uploadError: null,
		}
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return FunctionalMap;
	}

	/**
     *  Returns item lookup that shall be inserted to the Entity.get method
     *  @param {Number}     id          ID of the item
     *  @return {Array}                 Array if IDs that include ID of the item, ID of parent iten etc,,,,
     *                                  (see Entity,get() for details)
     */
    getLookup(id){
        return {
        	parent: window.application.project,
        	id: id,
        }
    }

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return DataList;
	}

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the request)
	 */
	async _fetchList(filter){
		return await window.application.project.getMaps(filter);
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		return {};
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		return '';
	}

	/**
	 *  Reloads the data
	 * 	@async
	 */
	async reload(){
		this.setState({uploadError: null});
		await super.reload();
	}

	/**
     *  Renders the right pane of the sidebar.
     */
    renderRightPane(){
        return (
        	<div className={style.main}>
        		<div className={style.uploader_row}>
        			<DataUploader
        				fileManager={this.state.item && this.state.item.data}
        				tooltip={t("The functional map must be saved in a special NPY file." +
        					" Use this facility to upload this.")}
        				inactive={this.isLoading}
        				error={this.state.uploadError}
        				onError={this.handleUploadError}
        				cssSuffix={style.uploader}
        				additionalIcons={[
        					<div
        						className={style.download_icon}
        						onClick={event => this.handleItemDownload(event, 'npy')}>
        						NPY
        					</div>,
        					<div
        						className={style.download_icon}
        						onClick={event => this.handleItemDownload(event, 'mat')}>
        						MAT
        					</div>,
        				]}
        			/>
        		</div>
        		<div className={style.map_viewer}>Rendering the map viewer...</div>
        	</div>	
        );
    }

    /**
     * 	Triggers when the upload error fails
     * 	@param {Error} error 		reason why the file upload failed.
     */
    handleUploadError(error){
    	this.setState({uploadError: error});
    }

    /**
     *  Triggers when the user tries to open the item for editing
     *  @param {SyntheticEvent}     event           The event to trigger.
     */
    async handleItemOpen(event){
    	this.setState({uploadError: null});
    	await super.handleItemOpen(event);
    }

    /**
     * 	Triggers when the user tries to download the file
     * 	@param {SyntheticEvent}		event 			The event to trigger.
     * 	@param {string} 			format 			File format: 'mat' or 'npy'
     */
    async handleItemDownload(event, format){
    	try{
    		this.reportListFetching();
    		let result = await this.state.item.download(format);
    		let resultUrl = URL.createObjectURL(result);
    		let link = document.createElement('a');
    		document.body.append(link);
    		link.href = resultUrl;
    		link.download = this.state.item.data.toString().replace(/\.npy$/, `.${format}`);
    		link.click();
    		link.remove();
    		URL.revokeObjectURL(resultUrl);
    		this.reportFetchSuccess(undefined);
    	} catch (error){
    		this.reportFetchFailure(error);
    	}
    }
}