import * as React from 'react';

import style from './style.module.css';


/**
 * 	Represents the child application in the iframe
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Module} 	application 			The application to open
 * 	@param {string} 	path 					Application path to open. If not set, the path will be selected
 * 	@param {string} 	cssSuffix 				Additional CSS classes to append
 *  @param {callback}   onApplicationMount      triggers when the child component of the root application has already
 *                                              been mounted.
 */
export default class ChildModuleFrame extends React.Component{

    constructor(props){
        super(props);
        this.handleFrameRendered = this.handleFrameRendered.bind(this);
    }

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
            <iframe src={url} className={classes} ref={this.handleFrameRendered}></iframe>
        );
	}

    /**
     *  Triggers when the iframe object has been completely rendered to the DOM <iframe> object.
     *  @param {FrameElement} iframe        the DOM object itself
     */
    handleFrameRendered(iframe){
        iframe.contentWindow.addEventListener("message", event => {
            if (event.origin !== window.location.origin){
                return;
            }
            let newEvent = {
                type: event.data.method,
                target: event.source.application,
                value: event.data.info,
            }
            let eventHandler = 'on' + newEvent.type[0].toUpperCase() + newEvent.type.slice(1);
            if (eventHandler in this.props){
                this.props[eventHandler](newEvent);
            }
        });
    }

}
