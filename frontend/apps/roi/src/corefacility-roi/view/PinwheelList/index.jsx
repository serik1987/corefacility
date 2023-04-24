import {translate as t} from 'corefacility-base/utils';
import ItemList from 'corefacility-base/view/ItemList';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import style from './style.module.css';


/** 
 * 	Manages the pinwheel list.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {iterable|null} 	items 			The item list, as it passed by the parent component.
 * 											Can be any iterable component. However, subtypes may require instance
 * 											of a certain class
 * 	@param {boolean} 		isLoading		true if the parent component is in 'loading' state.
 * 	@param {boolean} 		isError			true if the parent component is failed to reload this item list.
 * 	@param {callback} onItemAdd 	 			This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array} 			itemArray 		The item list transformed by the component to the Javascript array,
 * 											and hence can be mapped into array of ListItem components during the
 * 											rendering. Such a list contains not only those enitities that have been
 * 											passed during the reloading but also those passed during creation of
 * 											deletion of items.
 */
export default class PinwheelList extends ItemList{

    /** Renders content where single item will be shown
     *  @param {Pinwheel} pinwheel the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(pinwheel){
        return (
            <li key={pinwheel.id} className={style.root}>
                <span className={style.pinwheel_info}>X = {pinwheel.x}; Y = {pinwheel.y}</span>
                <Icon
                    onClick={event => this.handleEditPinwheel(event, pinwheel)}
                    type="mini"
                    inactive={this.props.isLoading}
                    tooltip={t("Change pinwheel position")}
                    src={<EditIcon/>}
                />
                <Icon
                    onClick={event => this.handleRemove(event, pinwheel)}
                    type="mini"
                    inactive={this.props.isLoading}
                    tooltip={t("Remove the pinwheel center")}
                    src={<RemoveIcon/>}
                />
            </li>
        );
    }

    /**
     *  Triggers when the user tries to edit the pinwheel center
     *  @async
     *  @param {SyntheticEvent} event                   The event that launched this method
     *  @param {Pinwheel}       pinwheel                Considering pinwheel
     */
    async handleEditPinwheel(event, pinwheel){
        let updatedPinwheel = await window.application.openModal('edit-pinwheel', {lookup: pinwheel.id});
        if (this.props.onItemSelect && updatedPinwheel){
            event.detail = updatedPinwheel;
            await this.props.onItemSelect(event);
        }
    }

}