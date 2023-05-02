import { Navigate } from "react-router-dom";

import {translate as t} from 'corefacility-base/utils';
import PaginatedList from 'corefacility-base/view/PaginatedList';
import ImagedListItem from 'corefacility-base/shared-view/components/ImagedListItem';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as SettingsIcon} from 'corefacility-base/shared-view/icons/settings.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import style from './style.module.css';

/** Represents the project list
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
 * 		@param {callback} onItemSelect		The function calls when the user clicks on a single item in the list (optional)
 * 
 * 	State:
 * 		@param {Array of Entity} itemArray 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class ProjectList extends PaginatedList{

    constructor(props){
        super(props);

        this.state = {
            ...this.state,
            redirectUrl: null,
        }
    }

    /** Renders content where single item will be shown
     *  @param {project} project the item to show in this content.
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(project){
        let governor = `${project.governor.surname} ${project.governor.name}`.trim();
        if (!governor){
            governor = project.governor.login;
        }

        let isGovernor = project.is_user_governor == true;
        let isSuperuser = window.application.user.is_superuser == true;
        let isPermissionRequired = window.SETTINGS.suggest_administration == true;

        return (
                <ImagedListItem
                    inactive={this.props.isLoading}
                    href={`/projects/${project.alias}/apps/`}
                    item={project}
                    img={project.avatar}
                    imageWidth={150}
                    imageHeight={150}
                    cssSuffix={style.main}
                >
                    <h2>{project.name}</h2>
                    <p>{project.root_group.name}</p>
                    <small>{t("Project leader")}: {governor}</small>
                    {(isGovernor || isSuperuser) && <div className={style.icons}>
                        <Icon
                            onClick={event => this.handleProjectSettings(event, project)}
                            tooltip={t("Project settings")}
                            src={<SettingsIcon/>}
                        />
                        {(!isPermissionRequired || isSuperuser) && <Icon
                            onClick={event => this.handleRemove(event, project)}
                            tooltip={t("Remove project")}
                            src={<RemoveIcon/>}
                        />}
                    </div>}
            </ImagedListItem>        
        );
    }

    render(){
        if (this.state.redirectUrl !== null){
            return <Navigate to={this.state.redirectUrl}/>
        }

        if (this.state.itemArray.length > 0){
            return super.render();
        } else {
            return <p><i>{t("There are no projects satisfying given criteria.")}</i></p>;
        }
    }

    handleProjectSettings(event, project){
        event.stopPropagation();
        this.setState({redirectUrl: `/projects/${project.alias}/`});
    }
	
}