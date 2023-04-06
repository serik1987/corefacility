import Button from 'corefacility-base/view/Button';

import style from './style.module.css';


/**
 * 	A menu item that is displayed on the left part of the screen rendered by the Sidebar component.
 * 	This component must be applied together with the Sidebar component.
 * 
 * 	Component props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}		current 		true, if this is a current menu item. The current item can't be either
 * 											clicked or redirected
 * 	@param {ReactComponent} icon 			an image to be displayed before the item name
 * 	@param {string}			text			the item text
 * 	@param {callback} 		onClick 		will be triggered when the user clicks on the menu item.
 * 	@param {string} 		href 			route to navigate to when the user clicks on the menu item; given that
 * 											onClick prop is fully absent
 * 	@param {boolean}		inactive		if true, the user can't click on a given menu item
 * 	@param {boolean}		disabled 		if true, the item looks as disabled and the user can't click on it
 * 	@param {string}			tooltip			tooltip to show when the user moves mouse to this tooltip
 * 	@param {string} 		cssSuffix 		Additional CSS classes to apply to the item
 * 
 * 	Component state:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	The component is fully stateless.
 */
export default class SidebarItem extends Button{

	/** Renders the button. This is an abstract method. So, when you extend the button,
	 *  don't forget to implement this method.
	 *  MIND about conditional rendering because the button may have two states depending
	 *  on the this.props.disabled value: enabled or disabled.
	 * 
	 * 	Don't override the render() method because such a method is responsible for proper
	 * 	work of href prop.
	 */
	renderContent(){
		let cssMain = `${style.main} sidebar-item`;
		if (this.props.current){
			cssMain += ` ${style.current}`;
		}
		if (this.props.inactive || this.props.disabled){
			cssMain += ` ${style.inactive}`;
		}
		if (this.props.disabled){
			cssMain += ` ${style.disabled}`;
		}
		if (this.props.cssSuffix){
			cssMain += ` ${this.props.cssSuffix}`;
		}

		return (
			<div className={cssMain} onClick={this.handleClick} title={this.props.tooltip}>
				<div className={style.icon_wrapper}>{this.props.icon}</div>
				<div className={`${style.text} sidebar-item-text`}>{this.props.text}</div>
			</div>
		);
	}

	/**
	 *  Triggers when the user clicks on the menu item
	 * 	@param {SyntheticEvent} event an event that triggers this action
	 */
	handleClick(event){
		if (!this.props.current){
			super.handleClick(event);
		}
	}

}