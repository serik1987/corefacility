import {translate as t} from '../../utils.mjs';

import PaginatedList from '../base/PaginatedList.jsx';
import ImagedListItem from '../base/ImagedListItem.jsx';



/** Represents paginated list of entities
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
* 		@param {Array|any} items 	 		The item list, as it passed by the parent component.
 * 											This item list doesn't modify when the parent component adds or removes items.
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload the list.
 * 		@param {callback} onItemSelect		Useless. Click on the user in the list will never lift up the state.
 * 											Otherwise, new route will be selected.
 * 
 * 	State:
 * 		@param {Array of Entity} items 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class UserList extends PaginatedList{

	/** Renders content where single item will be shown
	 * 	@param {User} user the user to be rendered
	 * 	@param {itemMode} true if we are going to add this item, false otherwise
	 */
	renderItemContent(user, itemMode){
		/* user.surname or user.name are not required fields, so they may equal to null */
		let userHeader = (`${user.surname || ''} ${user.name || ''}`).trim();
		if (userHeader === ''){
			userHeader = user.login;
		}

		return (<ImagedListItem
				key={user.id}
				img={user.avatar}
				imageWidth={75}
				imageHeight={75}
				item={user}
				href={`/users/${user.id}/`}
				inactive={this.isLoading}
				>
					<h2>{userHeader}</h2>
					<small>{t('Login')}: {user.login}</small>
		</ImagedListItem>);
	}

	render(){
		if (this.state.itemArray.length === 0 && !this.props.isLoading && !this.props.isError){
			return <p><i>{t("There are no users satisfying search criteria.")}</i></p>
		} else {
			return super.render()
		}
	}

}
