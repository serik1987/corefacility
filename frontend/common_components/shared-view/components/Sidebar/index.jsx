import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as SeparatorIcon} from 'corefacility-base/shared-view/icons/chevron.svg';

import Icon from '../Icon';
import style from './style.module.css';


/**
 *  Splits the remaining part of the screen into two parts. The left part is sidebar when the user can choose one of
 * 	several items. Tne right one is content, or working area.
 * 
 *  Children components:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	Controls that will be displayed on the right part of the sidebar.
 * 	
 * 	Component props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array of SidebarItem} items 			All items to display.
 * 
 * 	Component state:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} 			  isExpanded 		true, if the sidebar is expanded, false, if this is collapsed
 */
export default class Sidebar extends React.Component{

	constructor(props){
		super(props);
		this.handleSidebarChange = this.handleSidebarChange.bind(this);

		this.state = {
			isExpanded: true,
		}
	}

	render(){
		let widgetStyle = `${style.main} `;
		let sidebarTooltip;
		if (this.state.isExpanded){
			widgetStyle += style.expanded;
			sidebarTooltip = t("Collapse the sidebar");
		} else {
			widgetStyle += style.collapsed;
			sidebarTooltip = t("Expand the sidebar");
		}

		return (
			<div className={widgetStyle}>
				<div className={style.sidebar}>
					{this.props.items}
				</div>
				<div className={style.separator}>
					<Icon
						onClick={this.handleSidebarChange}
						tooltip={sidebarTooltip}
						src={<SeparatorIcon/>}
					/>
				</div>
				<div className={style.content}>
					{this.props.children}
				</div>
			</div>
		);
	}

	/**
	 *  Triggers when the user tries to change the sidebar state
	 * 	@param {SyntheticEvent} event 		the event triggered by the control item
	 */
	handleSidebarChange(event){
		this.setState({isExpanded: !this.state.isExpanded});
	}

}