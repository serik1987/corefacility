import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';
import Sidebar from 'corefacility-base/shared-view/components/Sidebar';
import SidebarItem from 'corefacility-base/shared-view/components/SidebarItem';
import {ReactComponent as AddIcon} from 'corefacility-base/shared-view/icons/add_simple.svg';

import FrameEditor from '../FrameEditor';

import style from './style.module.css';


/**
 * 	Represents the sidebar where the list of items is represented on the left side of the sidebar while content of the
 * 	individual item is on the right side. The method also supports dealing with routes.
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 *  @param  {Number}    lookup                  ID of the map to open on the right side. undefined will not open any map
 *                                              on the right side
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
export default class SidebarEditor extends FrameEditor{

    constructor(props){
        super(props);
        this.handleItemOpen = this.handleItemOpen.bind(this);

        this.state = {
            ...this.state,
            itemId: this.props.lookup ?? null,
            items: null,
        }
    }

    /**
     *  Returns item lookup that shall be inserted to the Entity.get method
     *  @param {Number}     id          ID of the item
     *  @return {Array}                 Array if IDs that include ID of the item, ID of parent iten etc,,,,
     *                                  (see Entity,get() for details)
     */
    getLookup(id){
        return [id];
    }

    /**
     *  Reloads the currently selected item
     *  @async
     *  @param  {Number} itemId         ID of the item to load. If undefined, the itemId will be taken from the
     *                                  component state. If undefined together with the itemId state, the method will
     *                                  do nothing.
     *  @return {Entity|boolean}        The reloaded entity on success or false in failure.
     */
    async reloadItem(itemId){
        itemId = itemId ?? this.state.itemId;
        try{
            this.reportListFetching();
            let item = await this.entityClass.get(this.getLookup(itemId));
            this.reportFetchSuccess(undefined);
            this.setState({item: item});
            return item;
        } catch (error){
            this.reportFetchFailure(error);
            return false;
        }
    }

    async reload(){
        await super.reload();
        if (this.state.itemId !== null){
            await this.reloadItem();
        }        
    }

    /**
     *  Renders the right pane of the sidebar
     */
    renderRightPane(){
        throw new NotImplementedError('renderRightPane');
    }

    /** Renders the item list.
     *  This function must be invoked from the render() function.
     */
    renderItemList(){
        let ItemList = this.entityListComponent;
        return (<ItemList
                    items={this.itemList}
                    isLoading={this.isLoading}
                    isError={this.isError}
                    ref={this.registerItemList}
                    itemId={this.state.itemId}
                    onItemOpen={this.handleItemOpen}
                    onItemSelect={this.handleSelectItem}
                    onItemRemove={this.handleItemRemove}
                />);
    }

	render(){
		return (
			<Sidebar
                cssSuffix={style.sidebar}
				items={
					<div className={style.main}>
                        <SidebarItem
                            onClick={this.handleAddButton}
                            icon={<AddIcon/>}
                            text={t("Add new data")}
                            inactive={this.isLoading}
                        />
						{this.renderItemList()}
					</div>
				}
			>
				{this.state.item && this.renderRightPane()}
                {this.state.item && !this.state.itemId && ''}
                {!this.state.itemId && <p>{t("Please, select the data from the left pane.")}</p>}
			</Sidebar>
		);
	}

    /**
     *  Triggers when the user tries to open the item for editing
     *  @param {SyntheticEvent}     event           The event to trigger.
     */
    async handleItemOpen(event){
        let entity = event.detail || event.value;
        this.setState({itemId: entity.id});
        let path = window.location.pathname;
        if (!path.endsWith('data/')){
            path = path.replace(this.state.itemId, entity.id);
        } else {
            path += `${entity.id}/`;
        }
        window.history.pushState(null, null, path);
        window.application.notifyStateChanged();
        await this.reloadItem(entity.id);
    }

    /**
     *  Triggers when the user tries to edit the item
     *  @param {SyntheticEvent}     event           The event to trigger.
     */
    async handleSelectItem(event){
        let entity = event.detail || event.value;
        if (!this.props.onItemChangeOpen){
            throw new Error("the onItemChangedOpen prop is required.");
        }
        let updatedEntity = await this.props.onItemChangeOpen(entity);
        if (!updatedEntity){
            return;
        }
        event.detail = updatedEntity;
        await super.handleSelectItem(event);
    }

}
