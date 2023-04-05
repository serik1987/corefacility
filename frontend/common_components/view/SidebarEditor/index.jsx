import {translate as t} from 'corefacility-base/utils';
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
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class SidebarEditor extends FrameEditor{

	render(){
		return (
			<Sidebar
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
				<p>Rendering the sidebar content...</p>
			</Sidebar>
		);
	}

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
