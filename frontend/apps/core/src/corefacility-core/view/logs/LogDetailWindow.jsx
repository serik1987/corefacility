import {useParams} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';

import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import NavigationWindow from '../base/NavigationWindow';
import Window404 from '../base/Window404';
import LogDetailForm from './LogDetailForm';


/** This is a wrapper for the _LogDetailWindow that transmits information about a Log ID from the location path
 */
export default function LogDetailWindow(props){
	let params = useParams();
	return <_LogDetailWindow {...props} logId={parseInt(params.lookup)} />
}


/** Provides the detailed information about a given log.
 * 
 * 	Props:
 * 	@param {Number} logId  		ID of the log which detailed information must be printed
 */
class _LogDetailWindow extends NavigationWindow{

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Log information");
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/logs/">{t("Logs")}</Hyperlink>,
			<p>{t("Log information")}</p>,
		];
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<LogDetailForm
				inputData={{lookup: this.props.logId}}
				on404={this.handle404}
				ref={this.setReloadCallback}
			/>
		);
	}

	render(){
		if (this.state.error404){
			return <Window404/>;
		}
		return super.render();
	}

}
