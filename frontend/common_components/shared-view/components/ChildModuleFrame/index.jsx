import * as React from 'react';

import style from './style.module.css';


/**
 * 	Represents the child application in the iframe
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Module} 	application 			The application to open
 * 	@param {string} 	path 					Application path to open. If not set, the path will be selected
 * 	@param {string} 	cssSuffix 				Additional CSS classes to append
 */
export default class ChildModuleFrame extends React.Component{

	render(){
        let classes = style.iframe;
        if (this.props.cssSuffix){
            classes += ` ${this.props.cssSuffix}`;
        }

        let path = null;
        if (this.props.path){
            path = this.props.path;
        } else if (window.SETTINGS.iframe_route){
            path = window.SETTINGS.iframe_route;
            window.SETTINGS.iframe_route = undefined;
        } else {
            path = '';
        }

        let url = `/ui/${this.props.application.uuid}/${path}/`.replace('//', '/')

		return (
            <iframe src={url} className={classes}></iframe>
        );
	}

}
