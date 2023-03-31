import * as React from 'react';
import {Navigate} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import ItemList from 'corefacility-base/view/ItemList';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import style from './style.module.css';


/** 
 * 	Renders all applications associated with a given project
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Project} 		project 		The related project
 * 	@param {iterable|null} 	items 			The item list, as it passed by the parent component.
 * 											Can be any iterable component. However, subtypes may require instance
 * 											of a certain class
 * 	@param {boolean} 		isLoading		true if the parent component is in 'loading' state.
 * 	@param {boolean} 		isError			true if the parent component is failed to reload this item list.
 * 	@param {callback} 		onItemSelect	The function calls when the user clicks on a single item in the list
 * 											(optional)
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array} 			itemArray 		The item list transformed by the component to the Javascript array,
 * 											and hence can be mapped into array of ListItem components during the
 * 											rendering. Such a list contains not only those enitities that have been
 * 											passed during the reloading but also those passed during creation of
 * 											deletion of items.
 * 
 * 	@param {Module} 		selectedApplication 	The application selected by the user.
 */
export default class InstalledProjectApplicationList extends ItemList{

	constructor(props){
		super(props);

		this.state = {
			...this.state,
			selectedApplication: null,
		}
	}

	/** Renders content where single item will be shown
	 * 	@param {Module} application the application to show in this content.
	 *  @return {Rect.Component} the component to render. The component must be a single
	 * 			item with the following conditions met:
	 * 				- the component must be an instance of the ListItem
	 * 				- its root element must be <li>
	 * 				- its key prop must be equal to item.id
	 * 				- its onClick prop must be equal to this.props.onItemSelect
	 */
	renderItemContent(application){
		return (
			<li
				key={application.uuid}
				className={style.item}
				onClick={event => this.handleItemSelect(event, application)}
			>
				<img src="/static/core/science.svg"/>
				<p>{application.name}</p>
			</li>
		);
	}

	/** Renders list of items itself
	 * 	@return {Rect.Component} the rendered component
	 */
	renderContent(){
		return (
			<ul className={style.item_list}>
				{ this.state.itemArray.map(item => this.renderItemContent(item)) }	
			</ul>
		);
	}

	render(){
		if (this.state.selectedApplication){
			return (
				<Navigate to={`/projects/${this.props.project.alias}/apps/${this.state.selectedApplication.alias}`}/>
			);
		} else if (!this.props.isLoading && !this.props.isError &&
			this.state.itemArray.length === 0 && this.props.project){
			return (
				<p className={style.no_items}>
					<i>{t("There are no applications added to the project.")}</i>
					{' '}
					{this.props.project.is_user_governor &&
						<Hyperlink href={`/projects/${this.props.project.alias}/appsettings/`}>
							{t("To add an application follow here.")}
						</Hyperlink>
					}
				</p>
			);
		} else {
			return super.render();
		}
	}

	/**
	 * 	Selects a proper item
	 * 	@param {SyntheticEvent}		event 		The item selected by the user
	 * 	@param {Module} 			application application selected by the user
	 */
	handleItemSelect(event, application){
		this.setState({selectedApplication: application});
	}

}
