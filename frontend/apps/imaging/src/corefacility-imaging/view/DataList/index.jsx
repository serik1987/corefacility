import {translate as t} from 'corefacility-base/utils';

import PaginatedList from 'corefacility-base/view/PaginatedList';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/close.svg';

import style from './style.module.css';


/**
 * 	Represents list of functional maps at the left part of the side bar.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {EntityPage|null} 	items 			The item list, as it passed by the parent component.
 * 												Must be an instance of EntityPage
 * 	@param {boolean} 			isLoading		true if the parent component is in 'loading' state.
 * 	@param {boolean} 			isError			true if the parent component is failed to reload the list.
 * 	@param {callback} 			onItemSelect	The function calls when the user clicks on a single item in the list
 *  @param {callback}           onItemRemove    Triggers when the user tries to remove the item
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array of Entity} 	itemArray 		full list of all items containing in all downloaded entity pages.
 * 												Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class DataList extends PaginatedList{

    /** Renders content where single item will be shown
     *  @param {FunctionalMap} functionalMap a functional map to display
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(functionalMap){
        return (
            <li key={functionalMap.id} className={style.item}>
                <p>{functionalMap.alias}</p>
                <Icon
                    onClick={event => this.handleEdit(event, functionalMap)}
                    inactive={this.props.isLoading}
                    tooltip={t("Edit")}
                    src={<EditIcon/>}
                />
                <Icon
                    onClick={event => this.handleRemove(event, functionalMap)}
                    inactive={this.props.isLoading}
                    tooltip={t("Remove")}
                    src={<RemoveIcon/>}
                />
            </li>
        );
    }

    /**
     *  Triggers when the user tries to edit the functional map.
     *  @param {SyntheticEvent} event               the event to trigger
     *  @param {FunctionalMap}  functionalMap       a functional map the user deals with.
     */
    handleEdit(event, functionalMap){
        if (this.props.onItemSelect){
            event.detail = functionalMap;
            this.props.onItemSelect(event);
        }
    }

}