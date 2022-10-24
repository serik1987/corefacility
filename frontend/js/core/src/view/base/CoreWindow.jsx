import {translate as t} from '../../utils.mjs';
import {NotImplementedError} from '../../exceptions/model.mjs';
import Loader from './Loader.jsx';
import Window from './Window.jsx';
import Icon from './Icon.jsx';
import styles from '../base-styles/CoreWindow.module.css';
import {ReactComponent as LogoImage} from '../base-svg/logo.svg';
import {ReactComponent as RefreshImage} from '../base-svg/refresh.svg';
import {ReactComponent as PersonImage} from '../base-svg/person.svg';
import {ReactComponent as SettingsImage} from '../base-svg/settings.svg';


/** The window of the main application
 *  Such window also have logo at the left top of the Web browser window
 *  as well as controls at the right top of the Web browser window
 *  The window has no props
 */
export default class CoreWindow extends Window{

	constructor(props){
		super(props);
		this.reloadingComponent = null;
		this.onReload = this.onReload.bind(this);
		this.setReloadCallback = this.setReloadCallback.bind(this);
	}

	/** Renders the area on the top of the Web browser window;
	 *  between the logo and the controls
	 *  @abstract
	 * 	@return {React.js component}
	 */
	renderControls(){
		throw new NotImplementedError("renderControls");
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		throw new NotImplementedError("renderContent");
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	onReload(event){
		if (this.reloadingComponent === null){
			throw new Error(`The 'Reload' button doesn't work because you did not define the 
				reloading component. To define the reloading component set ref={this.setReloadCallback} 
				inside the component tag.`);
		}
		this.reloadingComponent.reload();
	}

	setReloadCallback(component){
		if (!(component instanceof Loader)){
			throw new Error(`The reloading component must be an instance of the Loader class (see Loader.jsx)`)
		}
		this.reloadingComponent = component;
	}

	/** Provides rendering of the core window */
	render(){
		return (
			<div className={styles.window}>
				<header>
					<a href="/" className={styles.logo} title={t("Home Page")}>
						<LogoImage/>
					</a>
					<div className={styles.icons}>
						<Icon onClick={this.onReload} tooltip={t("Reload")} src={<RefreshImage/>}/>
						<Icon href="/profile/" tooltip={t("Account Settings")} src={<PersonImage/>}/>
						<Icon href="/settings/" tooltip={t("Application Settings")} src={<SettingsImage/>}/>
					</div>
					<div className={styles.controls}>
						{ this.renderControls() }
					</div>
				</header>
				<main>
					{ this.renderContent() }
				</main>
				{ this.renderAllModals() }
			</div>
		);
	}

}