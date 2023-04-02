import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {UnauthorizedError, ForbiddenError, NotFoundError,
	ServerSideError, NetworkError} from 'corefacility-base/exceptions/network';
import {ReactComponent as RefreshImage} from 'corefacility-base/shared-view/icons/refresh.svg';
import {ReactComponent as ErrorImage} from 'corefacility-base/shared-view/icons/error.svg';
	
import styles from './style.module.css';


/** The inline message bar that shows information about loading status or error. The message bar
 *  can exist in one of the following states: 'loading', 'error', none.
 * 		If the message bar is in none state, this is invisible and contains 'Ready.' message.
 * 		If the message bar is in 'loading' state, it is visible and shows black 'Loading...' message
 * 			preceded by the animated Refresh icon.
 * 		If the message bar is in 'error' state, it is visible and shows red error message preceeded by
 * 			the exclamation mark.
 * 	
 * 	Component props:
 * 		@param {boolean} isLoading 		true if the message bar is in 'Loading' state
 * 
 * 		@param {boolean} isError		true if the message bar is in 'error' state.
 * 										if both props (i.e., isLoading and isError) are true, the message
 * 										bar is considered to be in 'error' state
 * 
 * 		@param {string} loadingMessage 	the loading message to show if the message bar is in 'loading'
 * 										state. This prop is not applied if the message bar is not in the
 * 										loading state.
 * 
 * 		@param {Error} error 			The error class to be shown. This props is inaffected when the
 * 										message bar state is not 'error'
 * 
 * 		@param {boolean} isAnimatable	true if the state transition shall be animated, false otherwise
 * 
 * 		@param {boolean} isInline		true if the bar is inline (no padding, no border, inline-block)
 * 										false if the bar is not inline (padding - 114px on the left, 30px
 * 										on the right, very thin border below, block)
 * 
 * 		@param {string} cssSuffix 		Additional CSS classes defined by the parent
 * 
 * 	The component is fully stateless.
 * 
 * 	The network error 401 (Unauthorized), results to application reloading, errors 403 (Forbidden),
 * 	404 (Not Found) result to change of the application route. Any other errors will be printed.
 */
export default class MessageBar extends React.Component{

	DEFAULT_LOADING_MESSAGE = t("Loading...");

	/** The error message to be printed in the message bar.
	 *  The property uses 'message' field or the 'error' property
	 */
	get errorMessage(){
		if (typeof this.props.error === "string"){
			return this.props.error;
		}

		switch (this.props.error.constructor){
			case UnauthorizedError:
				window.location.reload();
				break;
			case ForbiddenError:
			case NotFoundError:
				window.location = "/";
				break;
			case ServerSideError:
			case NetworkError:
				break;
			default:
				console.error(this.props.error);
		}

		return this.props.error.message;
	}

	render(){
		let messageBoxClass;
		let message;
		let icon;
		let animatableClass = this.props.isAnimatable ? ` ${styles.animatable}` : '';
		let inlineClass = this.props.isInline ? ` ${styles.inline}` : '';
		let cssClasses = this.props.cssSuffix ? ` ${this.props.cssSuffix}` : '';

		if (this.props.isError){
			messageBoxClass = ` ${styles.is_opened} ${styles.is_error}`;
			message = this.errorMessage;
			icon = (<ErrorImage/>);
		} else if (this.props.isLoading){
			messageBoxClass = ` ${styles.is_opened} ${styles.is_loading}`;
			message = this.props.loadingMessage || this.DEFAULT_LOADING_MESSAGE;
			icon = (<RefreshImage/>);
		} else {
			messageBoxClass = '';
			message = t("Ready.");
			icon = null;
		}

		return (
			<div className={`${styles.message_bar}${messageBoxClass}${animatableClass}${inlineClass}${cssClasses} message_bar`}>
				{icon}
				<p>{message}</p>
			</div>
		);
	}

}