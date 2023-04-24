import * as React from 'react';

import style from './style.module.css';


/**
 * 	Represents the child application in the iframe.
 * 
 *  Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Module} 	application 			The application to open
 * 	@param {string} 	path 					Default application path to open
 * 	@param {string} 	cssSuffix 				Additional CSS classes to append
 *  @param {callback}   onApplicationMount      triggers when the child component of the root application has already
 *                                              been mounted.
 *  @param {callback}   onFetchList             Triggers when the user fetches the list using the ListEditor
 *  @param {callback}   onFetchSuccess          Triggers when the fetch is successful.
 *  @param {callback}   onFetchFailure          Triggers when the user failed to fetch the list using the ListEditor
 * 
 *  State:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {string}     path                    Current application path to open.
 */
export default class ChildModuleFrame extends React.Component{

    constructor(props){
        super(props);
        this.handleFrameRendered = this.handleFrameRendered.bind(this);

        this.state = {
            path: null,
        }
    }

	render(){
        let classes = style.iframe;
        if (this.props.cssSuffix){
            classes += ` ${this.props.cssSuffix}`;
        }

        let path = null;
        if (this.props.path){
            path = this.props.path;
        } else if (this.state.path){
            path = this.state.path;
        } else {
            path = '';
        }

        let url = `/ui/${this.props.application.uuid}/${path}/`.replace('//', '/')

		return (
            <iframe src={url} className={classes} ref={this.handleFrameRendered}></iframe>
        );
	}

    componentDidMount(){
        if (window.SETTINGS.iframe_route){
            this.setState({path: window.SETTINGS.iframe_route});
            window.SETTINGS.iframe_route = undefined;
            this._basePath = window.location.pathname;
        } else if (window.location.pathname.search('/apps/') !== -1) {
            let [basePath, baseAppPath] = window.location.pathname.split('/apps/', 2);
            let [appName, appPath] = baseAppPath.split('/', 2);
            window.history.replaceState(null, null, `${basePath}/apps/${appName}`);
            this._basePath = window.location.pathname;
            this.setState({path: appPath});
        }
    }

    componentDidUpdate(prevProps, prevState){
        if (this.state.path && this.props.path !== prevProps.path){
            this.setState({path: this.props.path});
            this._basePath = window.location.pathname;
        }
    }

    /**
     *  Triggers when the iframe object has been completely rendered to the DOM <iframe> object.
     *  @param {FrameElement} iframe        the DOM object itself
     */
    handleFrameRendered(iframe){
        if (iframe){
            this._basePath = window.location.pathname;
            this.__iframeListener = iframe.contentWindow.addEventListener("message", event => {
                if (event.origin !== window.location.origin){
                    return;
                }
                if (event.data.method === 'click'){
                    window.document.body.click();
                }
                if (event.data.method === 'pathChanged'){
                    let pathname = (this._basePath + event.data.info).replace('//', '/');
                    window.history.replaceState(null, null, pathname);
                    window.application.notifyStateChanged();
                }
                let newEvent = {
                    type: event.data.method,
                    target: event.data.target || event.source.application,
                    source: event.source.application,
                    value: event.data.info,
                }
                let eventHandler = 'on' + newEvent.type[0].toUpperCase() + newEvent.type.slice(1);
                if (eventHandler in this.props){
                    this.props[eventHandler](newEvent);
                }
            });
            this.__iframe = iframe;
        } else if (this.__iframe && this.__iframeListener) {
            this.__iframe.removeEventListener("message", this.__iframeListener);
        }
    }

}
