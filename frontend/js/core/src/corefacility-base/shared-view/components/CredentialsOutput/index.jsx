import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as CopyIcon} from 'corefacility-base/shared-view/icons/content-copy.svg';

import Icon from '../Icon';
import style from './style.module.css';


/**
 * Displays an important information followed by the 'Copy to Clipboard' button
 * 
 * The component has no props and no state. To output the credentials information
 * specify the component's children
 */
export default class CredentialsOutput extends React.Component{

	constructor(props){
		super(props);
		this.handleCopyToClipboard = this.handleCopyToClipboard.bind(this);
	}

	handleCopyToClipboard(event){
		try{
			let textArea = document.createElement('textarea');
			document.body.append(textArea);
			textArea.value = this.props.children;
			textArea.focus();
			textArea.select();
			document.execCommand('copy');
			textArea.remove();
		} catch (error){
			console.warn(error);
		}
	}

	render(){
		if (!this.props.children || !this.props.children.trim()){
			return (<p className={style.empty_box}><i>{t("Not defined.")}</i></p>);
		}

		return (
			<div className={style.box}>
				<p>{this.props.children}</p>
				<Icon
					onClick={this.handleCopyToClipboard}
					tooltip={t("Copy to clipboard")}
					src={<CopyIcon/>}
				/>
			</div>
		);
	}

}