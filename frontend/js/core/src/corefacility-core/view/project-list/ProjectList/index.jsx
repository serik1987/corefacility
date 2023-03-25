import {translate as t} from 'corefacility-base/utils';
import PaginatedList from 'corefacility-base/view/PaginatedList';


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
        console.log(project.toString());
        return <p>{project.name}</p>;
    }

    render(){
        if (this.state.itemArray.length > 0){
            return super.render();
        } else {
            return <p><i>{t("There are no projects satisfying given criteria.")}</i></p>;
        }
    }
	
}