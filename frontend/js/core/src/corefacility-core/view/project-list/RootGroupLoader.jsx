import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {NotFoundError} from 'corefacility-base/exceptions/network';
import Loader from 'corefacility-base/view/Loader';

import Project from 'corefacility-core/model/entity/Project';
import GroupUserEditor from 'corefacility-core/view/group-list/GroupUserEditor';
import CoreWindowHeader from 'corefacility-core/view/base/CoreWindowHeader';


/**
 * 	This is a special component that allows the _ProjectDetailWindow to attach the GroupUserEditor in order to
 * 	controls the users in the root group.
 * 
 * 	Component props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string}		projectAlias 			Alias of the project to lookup
 * 	@param {callback}	on404 					Will be triggered when no such project was found
 * 
 * 	Component state:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Project} 	project 				A project which root group shall be displayed
 * 	@param {boolean} 	isLoading				true if the project is going to be loaded
 * 	@para, {Exception}	error 					Error to display, if project loading has been failed.
 */
export default class RootGroupLoader extends Loader{

	constructor(props){
		super(props);
		this.__groupUserEditor = React.createRef();

		this.state = {
			project: null,
			isLoading: false,
			error: null,
		}
	}

	/**
	 *  A child component that manages the group users
	 */
	get groupUserEditor(){
		return this.__groupUserEditor.current;
	}

	/** Reloads the data. This method runs automatically when the componentDidMount.
	 * 	Also, you can invoke it using the imperative React principle
	 * 	@return {undefined}
	 */
	async reload(){
		if (this.state.isLoading){
			return;
		}

		if (this.state.project === null){
			try{
				this.setState({project: null, isLoading: true, error: null});
				let project = await Project.get(this.props.projectAlias);
				this.setState({project: project});
			} catch (error){
				if (error instanceof NotFoundError){
					this.props.on404();
					return;
				}
				this.setState({error: error});
			} finally {
				this.setState({isLoading: false});
			}
		} else {
			if (this.groupUserEditor){
				await this.groupUserEditor.reload();
			} else {
				console.warn("Failed to reload component because the child entity has not been loaded!");
			}
		}
	}

	render(){
		if (this.state.project === null){
			return (
				<CoreWindowHeader
					isLoading={this.state.isLoading}
					isError={this.state.error !== null}
					error={this.state.error}
					header={t("Project's root group")}
				/>
			);
		} else {
			return (
				<GroupUserEditor
					group={this.state.project.root_group}
					name={this.state.project.root_group.name}
					on404={this.props.on404}
					ref={this.__groupUserEditor}
				/>
			);
		}
	}

}