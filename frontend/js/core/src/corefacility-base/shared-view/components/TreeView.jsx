import * as React from 'react';

import TreeItem from 'corefacility-base/model/tree/TreeItem';

import TreeViewItem from './TreeViewItem';


/** The widget allows to operate with the TreeItem model. It allows to expand and contract the tree view.
 * 
 *  Parent-controlled and user-controlled mode.
 *  -------------------------------------------
 *  If you assing the value prop of the TreeView, the TreeView switches to the parent-controlled mode: its value
 *  is solely controlled by the state of the parent widget. If the user selects the node, the node will not be
 *  selected until parent changes the node.
 * 
 *  If you left the value prop undefined, the TreeView is in user-controlled mode. The user can freely select
 *  any node of the tree
 * 
 *  Node addresses
 *  --------------------------------------------
 *  Node address is used to unambigiously identify the node within the tree. The node address is Javascript array
 *  satisfying the following rules:
 *  1. Node address for the root node is an empty array
 *  2. Node address for the child node can be revealed by the node index within the parentNode.children array to
 *  the end of parent node's node address.
 * 
 *  Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {TreeItem} tree                          The root node of the tree
 *  @param {boolean} inactive                       If the tree is inactive, all its node ignore any user events.
 *  @param {TreeItem} defaultValue                  Node value at the construction time
 *                                                  Useless in parent-controlled mode.
 *  @param {callback} onInputChange                 Triggers when the user input was changed. The only function argument
 *                                                  is an arbitrary object containing value and target.value fields
 *                                                  with an entity selected by the user.
 *  --------------------------------------------------------------------------------------------------------------------
 * 
 *  State:
 *  --------------------------------------------------------------------------------------------------------------------
 *  Here is general (tree-related) state fields
 *  @param {Entity} value                           The value selected by the user. Useless for parent-controlled mode.
 * 
 *  Some state fields are tightly connected wuth so called "node address" (see above for detailed 
 *  information about the node address). For the sake of simplicity, let's recap that the node address is an integer
 *  array that is used to undoubtedly identify one single node within the tree. Two tree nodes always have different
 *  node addresses.
 * 
 *  The state of the tree is combination of states of single tree nodes. Each state field is written in the form:
 *  <node-array>.<state-suffix)>
 *  where node-array is a string that contains all node address members separated by the dot and state-suffix is an
 *  arbitrary string that doesn't contain a dot.
 * 
 *  Mentioned below are state suffices for node-related states:
 *  @param {boolean} isOpened                       true if the tree node is expanded, false if this is contracted.
 *  @param {TreeItem.ChildrenState} childrenState   This is a technical state that is necessary to automatically start
 *                                                  rendering during the branch expansion/contraction
 *  --------------------------------------------------------------------------------------------------------------------
 */
export default class TreeView extends React.Component{

    constructor(props){
        super(props);
        this.handleStateChange = this.handleStateChange.bind(this);
        this.loadChildren = this.loadChildren.bind(this);
        this.handleNodeSelect = this.handleNodeSelect.bind(this);

        this.state = {
            value: null,
        }

        if (this.props.defaultValue){
            this.state.value = this.props.defaultValue;
        }
    }

    get value(){
        let value = null;
        if (this.props.value === undefined){
            value = this.state.value;
        } else {
            value = this.props.value;
        }
        return value;
    }

    /** Gets the state field for a given tree node
     *  @param {Array of Number} nodeAddress        Address of this node
     *  @param {string} suffix                      The state suffix
     *  @return {any}                               the field value
     */
    getNodeState(nodeAddress, suffix){
        return this.state[`${nodeAddress.join(".")}.${suffix}`];
    }

    /** Sets the state field for a given tree node
     *  @parram {Array of Number} ndoeAddress       Address of this node
     *  @param {string} suffix                      The state suffix
     */
    setNodeState(nodeAddress, suffix, value){
        this.setState({
            [`${nodeAddress.join(".")}.${suffix}`]: value,
        });
    }

    /** Loads the node children
     *  @async
     *  @param {TreeItem} node      Nodes which children have to be loaded
     *  @param {Array} nodeAddress  Address of this node
     */
    async loadChildren(node, nodeAddress){
        this.setNodeState(nodeAddress, "childrenState", node.childrenState);
        await node.loadChildren();
        this.setNodeState(nodeAddress, "childrenState", node.childrenState);
    }

    /** Processes item state changed switched by the user.
     * 
     *  @param {TreeItem} node          The node that has been opened or closed by the user.
     *  @param {Array} nodeAddress      Address of this node.
     *  @param {boolean} isOpened       The desired node state.
     */
    handleStateChange(node, nodeAddress, isOpened){
        this.setNodeState(nodeAddress, "isOpened", isOpened);
        if (isOpened && node.childrenState === TreeItem.ChildrenState.readyToLoad){
            this.loadChildren(node, nodeAddress);
        }
    }

    /** Triggers when the node is selected given that no value prop was set.
     *  @param {TreeItem} node          The node selected by the user.
     *  @param {Array} nodeAddress      Address of this node.
     */
    handleNodeSelect(node, nodeAddress){
        this.setState({value: node.entity});
        if (this.props.onInputChange){
            let eventData = {value: node.entity, target: {value: node.entity}};
            this.props.onInputChange(eventData);
        }
    }

    /** Renders a single node
     *  @param {TreeItem} node          The node to be rendered
     *  @param {Array} nodeAddress      Address of this node
     *  @param {boolean} isBranchOpened true if the branch should be opened, false otherwise
     *  return {React.Component}        The TreeViewItem component that corresponds to this node.
     */
    _renderNode(node, nodeAddress, isBranchOpened){
        return <TreeViewItem
                content={node}
                nodeAddress={nodeAddress}
                isOpened={isBranchOpened}
                inactive={this.props.inactive}
                isSelected={node.entity === this.value}
                onStateChange={this.handleStateChange}
                onChildrenReload={this.loadChildren}
                onNodeSelect={this.handleNodeSelect}
            />
    }

    /** Renders a particular branch inside the tree
     * 
     *  @param {TreeItem} the branch to be rendered
     *  @param {Array of Number} nodeAddress the Address of the branch to be displayed
     *  @return {Array of Rect.Component} list of components to be rendered.
     */
    _renderBranch(branch, nodeAddress){
        let isBranchOpened = this.getNodeState(nodeAddress, "isOpened") ?? false;
        let branchComponents = [];

        if (isBranchOpened && branch.childrenState === TreeItem.ChildrenState.ready){
            branchComponents = [].concat(branch.children.map((childNode, childNodeIndex) => {
                let childNodeAddress = [...nodeAddress, childNodeIndex];
                return this._renderBranch(childNode, childNodeAddress);
            }));
        }

        branchComponents.unshift(this._renderNode(branch, nodeAddress, isBranchOpened));

        return branchComponents;
    }

    /** Renders the whole tree
     */
    render(){
        return (
            <div>
                {this._renderBranch(this.props.tree, [])}
            </div>
        );
    }

}