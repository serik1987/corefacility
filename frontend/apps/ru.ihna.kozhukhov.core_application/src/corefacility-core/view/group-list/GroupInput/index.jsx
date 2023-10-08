import {translate as t} from 'corefacility-base/utils';
import EntityState from 'corefacility-base/model/entity/EntityState';
import Group from 'corefacility-base/model/entity/Group';
import SmartEntityInput from 'corefacility-base/view/SmartEntityInput';
import Icon from 'corefacility-base/shared-view/components/Icon';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import MessageBar from 'corefacility-base/shared-view/components/MessageBar';
import {ReactComponent as CloseIcon} from 'corefacility-base/shared-view/icons/close.svg';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import {ReactComponent as AddIcon} from 'corefacility-base/shared-view/icons/add_simple.svg';

import style from './style.module.css';


/**
 *	Allows the user to select a given group input from the group input list or to tell your parent widget that he
 * 	want to create new group.
 * 
 * 	Component props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} globalSearch			Turns on global search mode. In global search mode the user can view all
 *                                          groups in the list and select any group. Also, global search mode doesn't
 *                                          allow user to create new group.
 * 
 *  @param {boolean} groupAddFeature        Turns on the group add feature. The group add feature allows the user to
 *                                          add new group together with adding or modifying the form object, but
 *                                          requires similar implementation on the backend
 * 
 *  @param {boolean} mustBeGovernor         Displays only those projects where the user is governor
 * 
 *	@param {callback} onInputChange			The function invoked each time when the user selects a given widget,
 * 											discards any previous selection or chooses to select another widget.
 * 
 *	@param {Group} value 					When this value is set, the widget is stated to be in parent-controlled
 * 											mode, which means that any user selection will not be applied until they
 * 											are approved by the parent.
 * 
 *	@param {string} defaultValue			At the first rendering, the input box value will be set to the value
 * 	                                        of this prop. During each next rendering this prop has no effect
 *                                          This prop is overriden by the value prop
 * 
 *	@param {string} error 					The error message that will be printed when validation fails
 * 
 *	@param {string} tooltip					Detailed description of the field
 * 
 *  @param {string} placeholder		        The placeholder to output
 * 
 *	@param {boolean} disabled				When the input box is disabled, it is colored as disabled and the user can't
 * 											enter any value to it
 * 									
 * 	@param {boolean} inactive				When the input box is inactive, the user can't enter value to it
 * 
 *  @param {String} cssSuffix   	        Additional CSS classes to apply
 * 
 * 
 * 	Component state:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  @param {Entity} value                   A certain group selected by the user
 * 
 *  @param {string} rawSearchTerm           Unprocessed search string entered by the user
 * 
 *  @param {string} searchTerm              Processed search string entered by the user
 * 
 *  @param {boolean} isEdit                true if the widget is in edit state, false otherwise
 */
export default class GroupInput extends SmartEntityInput{

    constructor(props){
        super(props);
        this.handleGroupCreate = this.handleGroupCreate.bind(this);
    }

    /** Returns class of the entity which list must be downloaded from the external server
     *  using this component
     */
    get entityClass(){
        return Group;
    }

    /** Uses the component props and state to identify search params
     *  @param {object} props props that must be used to calculate the filter.
     *  @param {object} state the state that must be used to calculate the filter
     *  @return {object} the filter that will be passed as a single argument to the
     *  entity's find function
     */
    deriveFilterFromPropsAndState(props, state){
        let searchParams = {profile: 'light'};
        if (state.searchTerm){
            searchParams.q = state.searchTerm;
        }
        if (props.globalSearch){
            searchParams.all = '';
        }
        if (props.mustBeGovernor){
            searchParams.mustbegovernor = '';
        }
        return searchParams;
    }

    /** The function transforms the filter props and state to
     *  identify the filter identity. The filter identity is a short string that
     *  follow the following conditions:
     *      - if the user did not adjust the filter, the string remains to be unchanged
     *      - if the user adjusted at least on of the filter property, the string changes
     *  @return {object} props props for which the filter must be calculated
     *  @return {object} state state for which the filter must be calculated
     *  @return {string} the filter identity
     */
    deriveFilterIdentityFromPropsAndState(props, state){
        let filterIdentity;
        if (props.globalSearch){
            filterIdentity = 'global://';
        } else {
            filterIdentity = 'local://';
        }
        if (props.mustBeGovernor){
            filterIdentity += "governor@";
        }
        if (state.searchTerm){
            filterIdentity += state.searchTerm;
        }
        return filterIdentity;
    }

    /**
     * Renders the widget given that this is in non-edit mode
     * @return {React.Component}
     */
    renderNonEditMode(){
        let icon, drawBorder, header, text;
        if (this.value === null){
            icon = <CloseIcon/>;
            drawBorder = true;
            header = t("Scientific group has not been selected");
            text = <Hyperlink
                onClick={this.handleEditMode}
                inactive={this.props.inactive}
                disabled={this.props.disabled}
            >
                {t("Click here to select the group")}
            </Hyperlink>;
        } else if (this.value.state === EntityState.creating){
            icon = <AddIcon/>;
            drawBorder = true;
            header = this.value.name;
            text = t("Create new group");
        } else {
            icon = <img src={this.value.governor.avatar}/>;
            drawBorder = false;
            header = this.value.name;

            text = `${this.value.governor.surname} ${this.value.governor.name}`.trim();
            if (!text){
                text = this.value.governor.login;
            }
        }

        if (drawBorder){
            icon = <div className={style.icon_border}>{icon}</div>
        }


        return (
            <div className={style.group_overview}>
                <div className={style.group_icon}>{icon}</div>
                <div className={style.info_area}>
                    <div className={style.header}>{header}</div>
                    <div className={style.text}>{text}</div>
                </div>
                {!this.props.disabled && <div className={style.edit_button}>
                    <Icon
                        onClick={this.handleEditMode}
                        inactive={this.props.inactive}
                        tootip={t("Change the scientific group")}
                        src={<EditIcon/>}
                    />
                </div>}
            </div>
        );
    }

    /**
     *  Renders content that shows when you open the context menu.
     */
    renderDropDownContent(){
        let messageBarRequired = 
            this.isError ||
            this.isLoading && (!this.itemList || this.itemList.totalCount === 0);

        let itemListExists = this.itemList && this.itemList.totalCount > 0;
        let groupAddFeature = this.props.groupAddFeature ?? true;

        return (
            <div className={style.group_list_box}>
                {messageBarRequired && <MessageBar
                    isLoading={this.isLoading}
                    isError={this.isError}
                    error={this.error}
                    isAnimatable={false}
                    isInline={true}
                />}
                {itemListExists && [
                    <div className={style.group_list_prompt}>
                        {t("Choose a proper scientific group from the list below")}
                    </div>,
                    <div className={style.group_list}>
                        {[...this.itemList].map(group => {
                            let supervisorName = `${group.governor.surname} ${group.governor.name}`.trim();
                            if (supervisorName === ''){
                                supervisorName = group.governor.login;
                            }

                            return (
                                <div
                                    className={style.group_overview}
                                    onClick={event => this.handleGroupSelect(event, group)}
                                >
                                    <div className={style.group_icon}>
                                        <img src={group.governor.avatar}/>
                                    </div>
                                    <div className={style.info_area}>
                                        <div className={style.header}>{group.name}</div>
                                        <div className={style.text}>{supervisorName}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ]}
                {groupAddFeature && <div className={style.group_overview} onClick={this.handleGroupCreate}>
                    <div className={style.group_icon}>
                        <div className={style.icon_border}>
                            <AddIcon/>
                        </div>
                    </div>
                    <div className={style.info_area}>
                        <div className={style.header}>{t("Create new group")}</div>
                        {!this.state.searchTerm && <div className={style.text}>
                            <i>{t("You must type the name of this new group.")}</i>
                        </div>}
                    </div>
                </div>}
            </div>
        );
    }

    /**
     *  Triggers when the user selects a given group
     *  @param {SyntheticEvent} event the event that has triggered this handler
     *  @param {Group} group a particular group selected by the user
     */
    handleGroupSelect(event, group){
        this.setState({
            isOpened: false,
            value: group,
        });
        if (this.props.onInputChange){
            event.value = event.target.value = group;
            this.props.onInputChange(event);
        }
    }

    /**
     *  Triggers when the user tries to create new group
     *  @param {SyntheticEvent} event an event that creates new group
     */
    handleGroupCreate(event){
        if (!this.state.searchTerm){
            return;
        }

        let group = new Group({name: this.state.searchTerm});
        this.handleGroupSelect(event, group);
    }

}