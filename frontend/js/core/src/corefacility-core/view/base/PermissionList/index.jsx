import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';

import ItemList from 'corefacility-base/view/ItemList';
import Label from 'corefacility-base/shared-view/components/Label';
import ComboBox from 'corefacility-base/shared-view/components/ComboBox';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import GroupInput from 'corefacility-core/view/group-list/GroupInput';

import style from './style.module.css';


/** 
 * 	This is the base class for project and application permissions
 * 
 * 	Props:
 * 		@param {iterable|null} items 		The item list, as it passed by the parent component.
 * 											Can be any iterable component. However, subtypes may require instance
 * 											of a certain class
 *      @param {array of object} accessLevelList  list of all access levels; just for the combo box.
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload this item list.
 *      @param {callback} onPermissionAdd   Triggerw when the user add a certain group permission. Callback argument:
 *          @param {int} groupId            ID for the group which permissions must be added
 *      @param {callback} onPermissionSet   Triggers when the user sets a certain permission. The callback arguments:
 *          @param {int} groupId            ID for the group which permissions must be added
 *          @param {int} levelId            ID for the access level
 *      @param {callback} onPermissionRemove Triggers when the user tries to remove permission
 *          @param {int} groupId            ID for the group that user tries to exclude from the access control list
 * 
 * 	State
 * 		@param {Array} itemArray 			The item list transformed by the component to the Javascript array, and hence
 * 											can be mapped into array of ListItem components during the rendering.
 * 											Such a list contains not only those enitities that have been passed during the
 * 											reloading but also those passed during creation of deletion of items.
 */
export default class PermissionList extends ItemList{

    constructor(props){
        super(props);
        this.selectAddGroup = this.selectAddGroup.bind(this);

        this.state = {
            ...this.state,
            predefinedValueList: {},
            selectedGroup: null,
            selectedGroupError: null,
        }
    }

    /**
     *  Returns the value list
     */
    get valueList(){
        if (this.__valueList === undefined){
            this.__valueList = this._generateValueList();
        }
        return this.__valueList;
    }

    /**
     *  Removes all derivated states
     */
    flushState(){
        this.setState({
            predefinedValueList: {},
            selectedGroup: null,
            selectedGroupError: null,
        });
    }

    /**
     *  Changes the access level right
     *  @async
     *  @param {Group} groupId              ID of the group which access level must be changed
     *  @param {int} levelId                ID for the access level
     */
    async changeAccessRight(groupId, levelId){
        try{
            this.setState({predefinedValueList: {[groupId]: levelId}});
            if (this.props.onPermissionSet){
                await this.props.onPermissionSet(groupId, levelId);
            }
        } catch (error){

        } finally {
            this.flushState();
        }
    }

    /**
     *  Selects a group to add to the access control list
     *  @param {SyntheticEvent} event       The event that has triggered this action
     */
    selectAddGroup(event){
        this.flushState();
        this.setState({selectedGroup: event.value});
    }

    /**
     *  Adds new access right
     *  @async
     */
    async addAccessRight(){
        let group = this.state.selectedGroup;
        this.flushState();
        if (group === null){
            this.setState({selectedGroupError: t("Please, select a group which permission must be added")});
        }
        for (let item of this.state.itemArray){
            if (item.group.id === group.id){
                this.setState({selectedGroupError: t("You have already add this group to the access control list")});
                return;
            }
        }
        if (this.props.onPermissionAdd){
            await this.props.onPermissionAdd(group.id);
        }
    }

    /**
     *  Removes an access right for the group
     *  @async
     *  @param {Group} group        A group which access right must be removed
     */
    async removeAccessRight(group){
        if (this.props.onPermissionRemove){
            this.props.onPermissionRemove(group.id);
        }
    }

    /**
     *  Modifies the item in the list
     *  @param {object} item        An object with the following properties
     *      @param {Group} group        A group which permission must be modified
     *      @param {AccessLevel} level  New level to be set
     */
    modifyItem(item){
        let {group, level} = item;
        let items = this.state.itemArray;
        for (let item of items){
            if (item.group.id === group.id){
                item.level = level;
            }
        }
        this.setState({itemArray: [...items]});
    }

    /**
     * Removes the entity from the list
     * @param {int} groupId the group to remove
     */
    removeItem(groupId){
        let entityIndex = -1;
        for (let index in this.state.itemArray){
            if (this.state.itemArray[index].group.id === groupId){
                entityIndex = index;
                break;
            }
        }
        if (entityIndex !== -1){
            this.state.itemArray.splice(entityIndex, 1);
        }
        this.setState({
            itemArray: [...this.state.itemArray],
        });
    }

    /** 
     *  Renders content where single item will be shown
     *  @param {Entity} item the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(item){
        let {group, level} = item;
        let isRootGroup = typeof group.tag === 'object' && group.tag.readOnlyPermission;

        let components = [
            <Label>{group.name}</Label>,
            <ComboBox
                valueList={this.props.accessLevelList}
                onInputChange={event => this.changeAccessRight(group.id, event.value)}
                value={this.state.predefinedValueList[group.id] ?? level.id}
                inactive={this.props.isLoading}
                disabled={isRootGroup}
            />,
        ];

        if (!isRootGroup){
            components.push(<Icon
                onClick={event => this.removeAccessRight(group)}
                inactive={this.props.isLoading}
                tooltip={t("Remove this permission")}
                src={<RemoveIcon/>}
            />);
        } else {
            components.push(<div></div>);
        }

        return components;
    }

    renderContent(){
        return (
            <div className={style.main}>
                <div className={style.permission_list}>
                    { this.state.itemArray.map(item => this.renderItemContent(item)) }
                    <Label>{t("New permission")}</Label>
                    <GroupInput
                        globalSearch={true}
                        groupAddFeature={false}
                        mustBeGovernor={false}
                        value={this.state.selectedGroup}
                        onInputChange={this.selectAddGroup}
                        error={this.state.selectedGroupError}
                        inactive={this.isLoading}
                    />
                    <div>
                        <PrimaryButton onClick={event => this.addAccessRight()}>{t("Add")}</PrimaryButton>
                    </div>
                </div>
            </div>
        );
    }

}