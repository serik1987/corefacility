import {Link} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';
import Loader from 'corefacility-base/view/Loader';
import Window from 'corefacility-base/view/Window';
import DropDownMenu from 'corefacility-base/shared-view/components/DropDownMenu';
import Icon from 'corefacility-base/shared-view/components/Icon';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import {ReactComponent as LogoImage} from 'corefacility-base/shared-view/icons/logo.svg';
import {ReactComponent as RefreshImage} from 'corefacility-base/shared-view/icons/refresh.svg';
import {ReactComponent as PersonImage} from 'corefacility-base/shared-view/icons/person.svg';
import {ReactComponent as SettingsImage} from 'corefacility-base/shared-view/icons/settings.svg';

import styles from './style.module.css';


/** The window of the main application
 *  Such window also have logo at the left top of the Web browser window
 *  as well as controls at the right top of the Web browser window
 *  The window has no props
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 */
export default class CoreWindow extends Window{

	constructor(props){
		super(props);
		this.reloadingComponent = null;
		this.onReload = this.onReload.bind(this);
		this.setReloadCallback = this.setReloadCallback.bind(this);
		this.handle404 = this.handle404.bind(this);
		this.handleLogout = this.handleLogout.bind(this);

		this.state = {
			error404: false
		}
	}

	/** If this property is true, the component can be reloaded.
	 *  The reloading works properly if ref={setReloadCallback}
	 * 	was set to true for at least one child component.
	 */
	get reloadable(){
		return true;
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
		if (!(component instanceof Loader) && component !== null){
			throw new Error(`The reloading component must be an instance of the Loader class (see Loader.jsx)`)
		}
		this.reloadingComponent = component;
	}

	/** Handles the 404 error by setting page 404
	 * 
	 * 	@return {undefined}
	 */
	handle404(){
		this.setState({error404: true});
	}

	handleLogout(event){
		document.cookie = "token=; Max-Age=-9999999; path=/";
		window.location.reload();
	}

	/** Provides rendering of the core window */
	render(){
		return (
			<div className={styles.window}>
				<header>
					<Link to="/" className={styles.logo} title={t("Home Page")}>
						<LogoImage/>
					</Link>
					<div className={styles.icons}>
						{this.reloadable && <Icon onClick={this.onReload} tooltip={t("Reload")} src={<RefreshImage/>}/>}
						<DropDownMenu
							caption={
								<Icon tooltip={t("Account Settings")} src={<PersonImage/>}/>
							}
							items={[
								!window.application.user.is_support && 
									<Hyperlink href="/profile/">{t("Profile")}</Hyperlink>,
								<Hyperlink href="/groups/">{t("Groups")}</Hyperlink>,
								<Hyperlink onClick={this.handleLogout}>{t("Logout")}</Hyperlink>,
							]}
						/>
						<DropDownMenu
							caption={
								<Icon tooltip={t("Application Settings")} src={<SettingsImage/>}/>
							}
							items={[
								window.application.user.is_superuser &&
									<Hyperlink href="/users/">{t("Users")}</Hyperlink>,
								window.application.user.is_superuser &&
									<Hyperlink href="/logs/">{t("Logs")}</Hyperlink>,
								window.application.user.is_superuser &&
									<Hyperlink href="/settings/">{t("Application Settings")}</Hyperlink>,
								<Hyperlink href="/sysinfo/">{t("System information")}</Hyperlink>,
								<Hyperlink href="/procinfo/">{t("Process list")}</Hyperlink>
							]}
						/>
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