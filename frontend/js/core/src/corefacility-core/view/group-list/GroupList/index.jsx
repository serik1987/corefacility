import {translate as t} from 'corefacility-base/utils';

import Label from 'corefacility-base/shared-view/components/Label';
import LabelInput from 'corefacility-base/shared-view/components/LabelInput';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as GroupLeaderIcon} from 'corefacility-base/shared-view/icons/star.svg';
import {ReactComponent as UsersIcon} from 'corefacility-base/shared-view/icons/person.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';
import PaginatedList from 'corefacility-base/view/PaginatedList';

import style from './style.module.css';


/** Represents paginated list.
 * 
 *  Paginated lists are entity lists that are downloaded from the server by small pieces.
 *  Such lists exists as instances of the EntityPage.
 *  The component allows to display several such pages as a single list and provide features
 * 	for downloading more pages and attaching them at the end of the list.
 * 
 * 	This component is unable to manage such lists, provide CRUD operations on them and even
 * 	download the first page. This is considered to be a feature of the parent component.
 * 
 * 	Props:
 * 		@param {EntityPage|null} items 		The item list, as it passed by the parent component.
 * 											Must be an instance of EntityPage
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload the list.
 *      @param {callback} onItemEdit        Triggers when the user tries to change the group name
 *      @param {callback} onUserRemove      Triggers when the user tries to remove itself from the group
 *      @param {callback} onItemRemove      Triggers when the user tries to remove the group
 * 
 * 	State:
 * 		@param {Array of Entity} items 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class GroupList extends PaginatedList{

    constructor(props){
        super(props);
        this.handleRemoveUserFromGroup = this.handleRemoveUserFromGroup.bind(this);
    }

    /** Renders content where single item will be shown
     *  @param {Entity} group the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(group){
        let allowToEdit = group.governor.id === window.application.user.id || window.application.user.is_superuser;

        return (
            <li className={style.main}>
                {allowToEdit && <LabelInput
                    value={group.name}
                    onInputChange={event => this.handleItemEdit(event, group)}
                    maxLength={256}
                    inactive={this.props.isLoading}
                />}
                {!allowToEdit && <Label>{group.name}</Label>}
                {group.governor.id === window.application.user.id && <Icon
                    src={<GroupLeaderIcon/>}
                    tooltip={t("You are the leader of this group")}
                    inactive={this.props.isLoading}
                    onClick={event => {}}
                />}
                <Icon
                    src={<UsersIcon/>}
                    tooltip={t("User list")}
                    inactive={this.props.isLoading}
                    href={`/groups/${group.id}/`}
                />
                {allowToEdit && <Icon
                    src={<RemoveIcon/>}
                    tooltip={t("Remove the group")}
                    inactive={this.props.isLoading}
                    onClick={event => this.handleRemove(event, group)}
                />}
                {!allowToEdit && <Icon
                    src={<RemoveIcon/>}
                    tooltip={t("Remove user from the group")}
                    inactive={this.props.isLoading}
                    onClick={event => this.handleRemoveUserFromGroup(event, group)}
                />}
            </li>
        );
    }

	render(){
		if (this.state.itemArray.length === 0 && !this.props.isLoading && !this.props.isError){
			return <p><i>{t("There are no groups satisfying the search criteria.")}</i></p>;
		} else {
			return super.render();
		}
	}

    /**
     * Triggers when the user finishes change of the group name
     * @param {SyntheticEvent} event        the event triggered by the child component
     * @param {Group} group                 group that is going to be changed
     * @return
     */
    handleItemEdit(event, group){
        if (group.name === event.value){
            return;
        }
        group.name = event.value;
        this.setState({items: this.state.items});
        event.detail = group;
        if (this.props.onItemSelect){
            this.props.onItemSelect(event);
        }
    }

    /**
     *  Triggers when the user tries to remove another user from the group
     *  @param {SyntheticEvent} event       event triggered by the child component
     *  @param {Group} group                a group from which the user must be excluded
     */
    handleRemoveUserFromGroup(event, group){
        event.detail = group;
        if (this.props.onUserRemove){
            this.props.onUserRemove(event);
        }
    }

}