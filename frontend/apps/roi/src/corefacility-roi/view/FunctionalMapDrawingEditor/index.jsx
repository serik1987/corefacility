import {createRef} from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import FrameEditor from 'corefacility-base/view/FrameEditor';

import style from './style.module.css';


/**
 * 	Connects the functional map drawers to the entity list
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback}	onItemAddOpen			This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 
 * 	@param {Number} 	reloadTime 				Timestamp of the last reload. Must be equal to 'reloadDate' state of
 * 												the parent 'Application' component
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 * 	@param {callback} onItemAddOpen 			This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class FunctionalMapDrawingEditor extends FrameEditor{

    constructor(props){
        super(props);
        this._graphicList = createRef();
    }

    /**
     *  Returns the graphic item list
     */
    get graphicItemListComponent(){
        throw new NotImplementedError('get graphicItemListComponent');
    }

    /**
     *  Returns the graphic list or null if no graphic list was attached.
     */
    get graphicList(){
        return this._graphicList.current;
    }

    render(){
        return (
            <div className={style.root}>
                <div className={style.graphic_list_wrapper}>
                    {window.application.functionalMap && this.renderGraphicItemList()}
                </div>
                <div className={style.list_wrapper}>
                    {this.renderItemList()}
                </div>
            </div>
        );
    }

    /**
     *  Adds new item
     *  @param {Entity} entity          The entity to add
     */
    async handleItemAdd(entity){
        await super.handleItemAdd(entity);
        this.graphicList.addItem(entity);
    }

    /** Handles clicking on a particular entity.
     *  This is a callback widget for the child component responsible
     *  for item modification. Don't forget to add this to the ItemList!
     *      @param {SyntheticEvent} event the event object
     *      @return {undefined}
     */
    async handleSelectItem(event){
        let entity = event.detail || event.value;
        await super.handleSelectItem(event);
        this.graphicList.changeItem(entity);
    }

    /**
     *  Triggers when the user is going to remove the item from the list
     *  @async
     *  @param {SyntheticEvent} event  the event triggered by the child component
     */
    async handleItemRemove(event){
        let entity = event.detail ?? event.value;
        if (await super.handleItemRemove(event)){
            this.graphicList.removeItem(entity);
        }
    }

    /**
     *  Draws amplitude and phase map with items depicted.
     */
    renderGraphicItemList(){
        let GraphicList = this.graphicItemListComponent;
        return (
            <GraphicList
                ref={this._graphicList}
                functionalMap={window.application.functionalMap}
                onFetchStart={() => this.reportListFetching()}
                onFetchSuccess={() => this.reportFetchSuccess(undefined)}
                onFetchFailure={error => this.reportFetchFailure(error)}
                cssSuffix={style.graphic_list}
                inactive={this.isLoading}
                itemList={this.itemList}
                onItemAdd={this.handleItemAdd}
                onItemChange={this.handleSelectItem}
                onItemRemove={this.handleItemRemove}
            />
        );
    }

}