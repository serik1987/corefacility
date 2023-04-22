import {translate as t} from 'corefacility-base/utils';
import ItemList from 'corefacility-base/view/ItemList';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';
import {ReactComponent as CropIcon} from 'corefacility-base/shared-view/icons/variables.svg';

import style from './style.module.css';


/** This is a base class for all widgets that represent list of entities
 *  Each entity despite of its source must have the 'id' property that reflects the entity unique ID.
 *  It doesn't matter for this particular component whether 'id' is string ID or number ID. Hoever this
 * 	is crucial that two different entities must have different IDs and two copies of the same entity must
 * 	have the same ID (even though they are two different Javascript objects).
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {iterable|null} 	items 			The item list, as it passed by the parent component.
 * 											Can be any iterable component. However, subtypes may require instance
 * 											of a certain class
 * 	@param {boolean} 		isLoading		true if the parent component is in 'loading' state.
 * 	@param {boolean} 		isError			true if the parent component is failed to reload this item list.
 * 	@param {callback} 		onItemAdd 		This method must be triggered the the user adds an entity to
 * 											the entity list by means of the entity list facility
 * 	@param {callback} 		onItemSelect	This method must be triggered when the user changes the entity
 * 											and wants editor to send the changes to the Web server.
 * 	@param {callback} 		onItemRemove 	This method must be triggered when the user removes the entity
 * 											and wants editor to send the changes to the Web Server.
 *  @param {callback}       applyRoi        This method must be triggered when the user tries to apply ROI to the
 *                                          current map.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array} 			itemArray 		The item list transformed by the component to the Javascript array,
 * 											and hence can be mapped into array of ListItem components during the
 * 											rendering. Such a list contains not only those enitities that have been
 * 											passed during the reloading but also those passed during creation of
 * 											deletion of items.
 */
export default class RectangularRoiList extends ItemList{

    /** Renders content where single item will be shown
     *  @param {RectangularRoi} roi the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     */
    renderItemContent(roi){
        return (
            <li key={roi.id} className={style.root}>
                <span className={style.roi_info}>
                    {t("Left")} = {roi.left}; {t("Right")} = {roi.right};{' '}
                    {t("Top")} = {roi.top}; {t("Bottom")} = {roi.bottom}
                </span>
                <Icon
                    onClick={event => this.applyRoi(event, roi)}
                    type="mini"
                    inactive={this.props.isLoading}
                    tooltip={t("Apply ROI")}
                    src={<CropIcon/>}
                />
                <Icon
                    onClick={event => this.handleEditRoi(event, roi)}
                    type="mini"
                    inactive={this.props.isLoading}
                    tooltip={t("Edit an existent ROI")}
                    src={<EditIcon/>}
                />
                <Icon
                    onClick={event => this.handleRemove(event, roi)}
                    type="mini"
                    inactive={this.props.isLoading}
                    tooltip={t("Remove the ROI")}
                    src={<RemoveIcon/>}
                />
            </li>
        );
    }

    /**
     *  Changes a given ROI.
     *  @async
     *  @param {SyntheticEvent} event                   An event that has triggered this action
     *  @param {RectangularRoi} roi                     ROI to deal with
     */
    async handleEditRoi(event, roi){
        let updatedRoi = await window.application.openModal('edit-rectangular-roi', {lookup: roi.id});
        if (this.props.onItemSelect){
            event.detail = updatedRoi;
            await this.props.onItemSelect(event);
        }
    }

    /**
     *  Applies the ROI
     *  @param {SyntheticEvent} event                   An event that has triggered this action
     *  @param {RectangularRoi} roi                     ROI to deal with 
     */
    applyRoi(event, roi){
        if (this.props.onApplyRoi){
            this.props.onApplyRoi(roi);
        }
    }

}