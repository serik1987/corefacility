import * as React from 'react';


import {translate as t} from 'corefacility-base/utils';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import CredentialsOutput from 'corefacility-base/shared-view/components/CredentialsOutput';

import style from './style.module.css';


/**
 * Provides a widget that allows the user to change his own password.
 * 
 * Props:
 * ---------------------------------------------------------------------------------------------------------------------
 * @param {PasswordManager}	value 			A special object that can change the user's password
 * @param {string} error 					The error message (props error has preference)
 * 
 * 
 * State:
 * ---------------------------------------------------------------------------------------------------------------------
 * @param {string} password 				The password to display when such a password has not been specified by the
 * 											value
 * @param {boolean} pending 				true if the password change is in progress
 * @param {string} error 					The error message (state error has preference)
 */
export default class PasswordChanger extends React.Component{

	constructor(props){
		super(props);
		this.handlePasswordChange = this.handlePasswordChange.bind(this);

		this.state = {
			password: null,
			pending: false,
			error: null,
		}
	}

	/**
	 * The password to display
	 */
	get password(){
		if (this.props.value === undefined){
			return this.state.password;
		} else {
			return this.props.value.value;
		}
	}

	/**
	 * The error message to display
	 */
	get error(){
		if (!this.props.error){
			return this.state.error;
		} else {
			return this.props.error;
		}
	}

	get inactive(){
		return this.props.inactive || this.state.pending;
	}

	render(){
		let className, content;

		if (this.password === null){
			className = style.password_unset;
			content = [
				<div className={style.password_modifier}>
					<p>{t("The password is not known")}</p>
					<Hyperlink onClick={this.handlePasswordChange} inactive={this.inactive}>
						{t("Change password")}
					</Hyperlink>
				</div>,
				this.error && <p className={style.error}>{this.error}</p>,
			];
		} else {
			className = style.password_set;
			content = <CredentialsOutput>{this.password}</CredentialsOutput>;
		}

		return <div className={className}>{content}</div>;
	}

	/**
	 * Defines actions to happen when the user changes his own password
	 */
	async handlePasswordChange(event){
		this.setState({pending: true, error: null});
		try{
			this.setState({password: await this.props.value.generate()});
		} catch (error){
			this.setState({error: error.message});
		} finally {
			this.setState({pending: false});
		}
	}

}