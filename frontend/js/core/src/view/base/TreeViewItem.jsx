import * as React from 'react';

import {translate as t} from '../../utils.mjs';
import TreeItem from '../../model/tree/tree-item.mjs';

import MessageBar from './MessageBar.jsx';
import Hyperlink from './Hyperlink.jsx';
import {ReactComponent as Chevron} from '../base-svg/chevron.svg';
import styles from '../base-styles/TreeViewItem.module.css';


/** Represents a single item of the tree view. Such an item is always the children of the TreeView, so there is no
 * 	necessity for you to create it alone.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {TreeItem} content 			The tree item to display
 * 	@param {Array} nodeAddress 			The address of the node. More detailed definition of what the node address is
 * 										is given in the TreeItem manual.
 * 	@param {boolean} isOpened 			true if the item is in opened state, false if this is in closed state.
 * 	@param {boolean} isSelected 		true if the node is selected by the user, false otherwise
 *  @param {boolean} inactive   If the tree is inactive, all its node ignore any user events.
 * 	@param {function} onStateChange		Triggers when the view item changes its state from opened to closed or vice
 * 										versa.
 * 										The function takes exactly three arguments:
 * 										@param {TreeItem} node 			The node to be processed
 * 										@param {Array} nodeAddress 		Address of this node
 * 										@param {boolean} isOpened 		The desired opened state.
 * 										Please note, the widget itself doesn't change its state upon the user click.
 * 										This is a parent's widget duty to do this.
 * 	@param {function} onChildrenReload	Triggers when the user clicks on "Try again" button causing all item children
 * 										to be reloaded.
 * 										The function takes exactly two arguments:
 * 										@param {TreeItem} node 			The node to be processed
 * 										@param {Array} nodeAddress 		Address of this node
 * 	@param {function} onNodeSelect 		Triggers when user selects the node. To select the node is to click on it
 * 										when the node is inactive.
 * 										The function takes exactly two arguments:
 * 										@param {TreeItem} node 			The node to be processed
 * 										@param {Array} nodeAddress 		Address of this nodeas
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	Optionally: if the entity attached to your TreeItem contains node_number field and the field equals to 0 the
 * 	expansion button will not be shown: a dot will be shown instead. If node number is not defined for your attached
 * 	entity this will be happened only when child nodes will be completely loaded and will be empty.
 */
export default class TreeViewItem extends React.Component{

	MIN_PADDING = 8;
	PADDING_INCREMENT = 24;

	constructor(props){
		super(props);
		this.handleOpenerClick = this.handleOpenerClick.bind(this);
		this.handleTryAgain = this.handleTryAgain.bind(this);
		this.handleItemClick = this.handleItemClick.bind(this);
	}

	/** Returns true if the node has children, false otherwise.
	 * 	The node is considered to have no children when one of the following conditions met
	 * 		(a) the node is attached to an entity which node_number property strictly equals to 0
	 * 		(b) the node children list has already been loaded and its length is 0
	 */
	hasChildren(){
		let hasChildren = true;
		if (this.props.content.entity.node_number === 0){
			hasChildren = false;
		}
		if (this.props.content.childrenState === TreeItem.ChildrenState.ready && 
				this.props.content.children.length === 0){
			hasChildren = false;
		}
		return hasChildren;
	}

	/** Handles user click on the opener button
	 */
	handleOpenerClick(event){
		if (this.props.inactive){
			return;
		}
		event.stopPropagation();
		if (this.props.onStateChange && this.hasChildren()){
			this.props.onStateChange(this.props.content, this.props.nodeAddress, !this.props.isOpened);
		}
	}

	/** Handles user click on the "Try again" message above the opener button
	 */
	handleTryAgain(event){
		if (this.props.inactive){
			return;
		}
		if (this.props.onChildrenReload){
			this.props.onChildrenReload(this.props.content, this.props.nodeAddress);
		}
	}

	handleItemClick(event){
		if (this.props.inactive){
			return;
		}
		if (this.props.onStateChange && this.hasChildren() && !this.props.isOpened){
			this.props.onStateChange(this.props.content, this.props.nodeAddress, true);
		}
		if (this.props.onNodeSelect && !this.props.isSelected){
			this.props.onNodeSelect(this.props.content, this.props.nodeAddress);
		}
	}

	render(){
		let node = this.props.content;
		let nodePadding = this.MIN_PADDING + this.PADDING_INCREMENT * this.props.nodeAddress.length;
		let nodeHasChildren = this.hasChildren();
		let nodeIsLoading = node.childrenState === TreeItem.ChildrenState.readyToLoad ||
			node.childrenState === TreeItem.ChildrenState.loading;
		let nodeIsError = node.childrenState === TreeItem.ChildrenState.error;
		let showError = this.props.isOpened && node.childrenState !== TreeItem.ChildrenState.ready;

		let itemClasses = styles.item;
		if (this.props.isOpened){
			itemClasses += ` ${styles.opened}`;
		}
		if (this.props.inactive){
			itemClasses += ` ${styles.inactive}`;
		}
		if (this.props.isSelected){
			itemClasses += ` ${styles.selected}`;
		}

		let itemOpenerClasses = styles.item_opener;
		if (node.entity.node_number === 0){
			itemOpenerClasses += ` ${styles.no_children}`;
		}


		return (
			<div className={styles.item_wrapper}>
				<div
					className={itemClasses}
					style={{paddingLeft: nodePadding + "px"}}
					onClick={this.handleItemClick}
					>
						<div className={styles.content_wrapper}>
							<div className={styles.item_opener} onClick={this.handleOpenerClick}>
								{nodeHasChildren && <div className={styles.chevron_wrapper}>
									<Chevron/>
								</div>}
								{!nodeHasChildren && <div className={styles.no_child_button}></div>}
							</div>
							<div className={styles.item_name}>{this.props.content.name}</div>
						</div>
				</div>
				{showError && <div className={styles.error_wrapper} style={{paddingLeft: nodePadding + "px"}}>
					<div className={styles.message_bar_wrapper}>
						<MessageBar
							isLoading={nodeIsLoading}
							isError={nodeIsError}
							error={node.childrenError}
							isAnimatable={false}
							isInline={true}
						/>
						{" "}
						{nodeIsError && <Hyperlink onClick={this.handleTryAgain}>{t("Try again.")}</Hyperlink>}
					</div>
				</div>}
			</div>
		);
	}

}