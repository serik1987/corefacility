import {translate as t} from 'corefacility-base/utils';
import PaginatedList from 'corefacility-base/view/PaginatedList';
import Label from 'corefacility-base/shared-view/components/Label';
import Icon from 'corefacility-base/shared-view/components/Icon';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import GroupUser from 'corefacility-core/model/entity/GroupUser';
import UserInput from 'corefacility-core/view/user-list/UserInput';

import SuggestedUserInput from '../SuggestedUserInput';
import style from './style.module.css';


/** Represents list of group members
 * 
 *  Paginated lists are entity lists that are downloaded from the server by small pieces.
 *  Such lists exists as instances of the EntityPage.
 *  The component allows to display several such pages as a single list and provide features
 *  for downloading more pages and attaching them at the end of the list.
 * 
 *  This component is unable to manage such lists, provide CRUD operations on them and even
 *  download the first page. This is considered to be a feature of the parent component.
 * 
 *  Props:
 *      @param {EntityPage|null} items      The item list, as it passed by the parent component.
 *                                          Must be an instance of EntityPage
 *      @param {Group} group                A group which list is representing
 *      @param {boolean} isLoading          true if the parent component is in 'loading' state.
 *      @param {boolean} isError            true if the parent component is failed to reload the list.
 *      @param {callback} onItemAdd         Triggers when the user adds an item
 *      @param {callback} onItemRemove      Triggers when the user removes an item
 * 
 *  State:
 *      @param {Array of Entity} items  full list of all items containing in all downloaded entity pages.
 *                                      Items from pages that are not downloaded yet were not shown.
 *  You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 *  high risk of state damaging. Use getters or setters instead
 */
export default class GroupUserList extends PaginatedList{

    constructor(props){
        super(props);
        this.handleItemSelect = this.handleItemSelect.bind(this);
        this.handleItemAdd = this.handleItemAdd.bind(this);

        this.state = {
            ...this.state,
            user: null,
            userSelectError: null,
        }
    }

    /**
     *  Identifies whether the user is allowed to modify another users in the list
     */
    get allowToModify(){
        if (!this._group){
            return false;
        }
        return window.application.user.is_superuser || this._group.governor.id === window.application.user.id;
    }

    /** Renders content where single item will be shown
     *  @param {GroupUser} the group user to be rendered
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(user){
        let name;
        if (user.name === null && user.surname === null){
            name = user.login;
        } else {
            name = (`${user.surname} ${user.name}`).trim();
        }

        this._group = user.parent;

        let allowToRemove = user.id !== user.parent.governor.id &&
            (this.allowToModify || window.application.user.id === user.id);

        return (
            <li className={style.item_box}>
                <Label>{name}</Label>
                {allowToRemove && <Icon
                    src={<RemoveIcon/>}
                    tooltip={t("Remove user from the list")}
                    inactive={this.props.inactive}
                    onClick={event => this.handleRemove(event, user)}
                />}
            </li>
        );
    }

    render(){
        return (
            <div>
                <h2>{t("Group users list")}</h2>
                {super.render()}
                {this.allowToModify && <div className={style.item_add_box}>
                    <SuggestedUserInput
                        group={this._group}
                        inactive={this.isLoading}
                        placeholder={t("New user name") + "..."}
                        value={this.state.user}
                        error={this.state.userSelectError}
                        onItemSelect={this.handleItemSelect}
                    />
                    <PrimaryButton inactive={this.isLoading} onClick={this.handleItemAdd}>
                        {t("Add")}
                    </PrimaryButton>
                </div>}
            </div>
        );
    }

    /**
     *  Triggers when the user selects another user to add
     *  @param {User} user      A user that were selected
     */
    handleItemSelect(user){
        this.setState({
            user: user,
            userSelectError: null,
        })
    }

    /**
     *  Triggers when the user is trying to add another user
     *  @param {SyntheticEvent} event   an event that has triggered this action
     */
    handleItemAdd(event){
        if (!this.state.user){
            this.setState({
                userSelectError: t("You haven't selected the user here."),
            });
            return;
        }
        
        if (this.props.onItemAdd){
            this.props.onItemAdd(new GroupUser({user_id: this.state.user.id}, this._group));
        }
        this.setState({user: null});
    }

}