import MessageBar from 'corefacility-base/shared-view/components/MessageBar';

import styles from './style.module.css';


/** Displays the window header together with error bar
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}			isLoading 		true if the message bar is in 'Loading' state
 * 	@param {boolean}			isError			true if the message bar is in 'error' state.
 * 												if both props (i.e., isLoading and isError) are true, the message
 * 												bar is considered to be in 'error' state
 * 	@param {Error}				error 			The error class to be shown. This props is inaffected when the
 * 												message bar state is not 'error'
 * 	@param {React.Component} 	header 			Header to display
 * 	@param {React.Component} 	aside 			Components to be displayed at the right of the header
 * 	@param {string} 			cssSuffix 		Additional CSS classes to apply
 * 
 * 	Children display information below the window header
 */
export default function CoreWindowHeader(props){
	const pendingClass = (props.isLoading || props.isError) ? styles.pending : null;
	let cssClasses = '';
	if (props.cssSuffix){
		cssClasses = ` ${props.cssSuffix}`;
	}

	return (
		<div className={`${styles.primary} window-header${cssClasses}`}>
			<aside>
				{ props.aside }
			</aside>
			<h1>{ props.header }</h1>
			<MessageBar
				isLoading={props.isLoading}
				isError={props.isError}
				error={props.error}
				isAnimatable={true}
			/>
			<article className={pendingClass}>
				{props.children}
			</article>
		</div>
	);

}