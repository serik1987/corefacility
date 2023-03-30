import {translate as t} from 'corefacility-base/utils';
import PaginatedList from 'corefacility-base/view/PaginatedList';
import Label from 'corefacility-base/shared-view/components/Label';
import CheckboxInput from 'corefacility-base/shared-view/components/CheckboxInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as DeleteIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import ProjectApplication from 'corefacility-core/model/entity/ProjectApplication';

import ApplicationInput from '../../ApplicationInput';
import style from './style.module.css';


/** 
 *  Represents list of applications connected to a particular project
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
 *      @param {Project} project            A project which list is shown
 * 		@param {EntityPage|null} items 		The item list, as it passed by the parent component.
 * 											Must be an instance of EntityPage
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload the list.
 *      @param {callback} onItemAdd         This method must be triggered the the user adds an entity to
 *                                          the entity list by means of the entity list facility
 *      @param {callback} onItemSelect      This method must be triggered when the user changes the entity
 *                                          and wants editor to send the changes to the Web server.
 *      @param {callback} onItemRemove      This method must be triggered when the user removes the entity
 *                                          and wants editor to send the changes to the Web Server.
 * 
 * 	State:
 * 		@param {Array of Entity} itemArray 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class ProjectApplicationList extends PaginatedList{

    constructor(props){
        super(props);
        this.handleItemAdd = this.handleItemAdd.bind(this);
        this.handleItemSelect = this.handleItemSelect.bind(this);

        this.state = {
            ...this.state,
            applicationToAdd: null,
            applicationToAddError: null,
        }
    }

    /** Renders content where single item will be shown
     *  @param {ProjectApplication} projectApplication the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(projectApplication){
        let itemElements = null;
        let applicationChanger = (
            <CheckboxInput
                label={projectApplication.name}
                value={projectApplication.is_enabled}
                inactive={this.isLoading}
                onInputChange={event => this.handleItemChange(event, projectApplication)}
            />
        );
        let applicationViewer = <Label>{projectApplication.name}</Label>;
        let disabledApplicationViewer = (
            <Label
                cssSuffix={style.disabled_app}
                tooltip={t("The application has been disabled by the system administrator.")}
            >
                {projectApplication.name}
            </Label>
        );
        let applicationRemover = (
            <Icon
                src={<DeleteIcon/>}
                inactive={this.isLoading}
                tooltip={t("Remove application from project")}
                onClick={event => this.handleRemove(event, projectApplication)}
            />
        );

        if (window.application.user.is_superuser){
            itemElements = [applicationChanger, applicationRemover];
        } else if (projectApplication.is_enabled) {
            itemElements = [applicationViewer, applicationRemover];
        } else {
            itemElements = [disabledApplicationViewer, <div></div>];
        }

        return itemElements;
    }

    /** Renders list of items itself
     *  @return {Rect.Component} the rendered component
     */
    renderContent(){
        return (
            <div className={style.main}>
                { this.state.itemArray.map(item => this.renderItemContent(item)) }
                <ApplicationInput
                    onInputChange={this.handleItemSelect}
                    value={this.state.applicationToAdd}
                    tooltip={t("Select an application to add to the project...")}
                    error={this.state.applicationToAddError}
                    inactive={this.isLoading}
                />
                <PrimaryButton onClick={this.handleItemAdd} inactive={this.isLoading}>
                    {t("Add")}
                </PrimaryButton>
            </div>
        );
    }

    /**
     *  Triggers when user selects an application to attach to the project
     */
    handleItemSelect(event){
        this.setState({
            applicationToAdd: event.value,
            applicationToAddError: null,
        });
    }

    /**
     *  Triggers when the user tries to add the button
     */
    async handleItemAdd(event){
        if (this.state.applicationToAdd === null){
            this.setState({
                applicationToAddError: t("Please, specify an application to add to the application list."),
            });
            return;
        }

        if (this.props.onItemAdd){
            let projectApplication = ProjectApplication.new(this.props.project, this.state.applicationToAdd);
            await this.props.onItemAdd(projectApplication);
            this.setState({
                applicationToAdd: null,
                applicationToAddError: null,
            });
        }
    }

    /**
     *  Triggers when the user tries to change the link between the project and the application
     *  @async
     *  @param {SyntheticEvent} event                       The event to trigger
     *  @param {ProjectApplication} ProjectApplicationList  The project application to change
     */
    async handleItemChange(event, projectApplication){
        projectApplication.is_enabled = event.value;
        if (this.props.onItemSelect){
            event.detail = projectApplication;
            await this.props.onItemSelect(event);
        }
    }

}