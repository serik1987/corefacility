import {NotImplementedError} from '../../exceptions/model.mjs';


/** Defines the Tree Item. The tree item is an item of the dynamic tree that  provides parent-to-child traversal and
 *  allows to upload tree children.
 * 
 *  Each tree node relates to a certain model object. The TreeItem can be used in the TreeViewer and TreeItemViewer
 *  components.
 */
export default class TreeItem{

    /** Creates the root node of the tree.
     *  During application of another of the instance branches will grow from this root node.
     * 
     *  @param {Entity} entity      the model object related to the tree. Please note that entity that return paginated
     *                              results in response to find() method are not supported
     */
    constructor(entity){
        this.ChildrenState = this.constructor.ChildrenState;

        this._entity = entity;
        this._children = null;
        this._childrenState = this.ChildrenState.readyToLoad;
        this._childrenError = null;
        this._parent = null;
    }

    /** Returns the model object attached to this tree node
     */
    get entity(){
        return this._entity;
    }

    /** Array of children nodes or null if children nodes have not been loaded yet
     */
    get children(){
        if (this._childrenState === this.ChildrenState.ready){
            return [...this._children];
        } else {
            return null;
        }
    }

    /** One of the following values:
     *      TreeItem.ChildrenState.readyToLoad          The children nodes have not been loaded by loadChildren() method
     *      TreeItem.ChildrenState.loading              The instance is loading the children now but response from the server
     *                                                  has not been received
     *      TreeItem.ChildrenState.error                The instance were loading in the past but error occured during the
     *                                                  loading.
     *      TreeItem.ChildrenState.ready                The children has been loaded from the Web server.
     */
    get childrenState(){
        return this._childrenState;
    }

    /** If the last children loading finished with error, this property contains error message.
     *  Otherwise, this property equals to null.
     */
    get childrenError(){
        return this._childrenError;
    }

    /** Human-readable name of the tree item
     */
    get name(){
        throw new NotImplementedError("get name");
    }

    /** Loads the children nodes from the external source. Please, note that children of the
     *  children are not children.
     */
    async loadChildren(){
        throw new NotImplementedError("loadChildren");
    }

    /** Converts whole tree to string (for the debugging purpose)
     */
    toString(){
        return this._branchToString(0);
    }

    /** Converts a given tree branch to string
     */
    _branchToString(treeLevel){
        let string = "";
        for (let level = 0; level < treeLevel; level++){
            string += "+";
        }
        string += " " + this._nodeToString() + "\n";
        if (this.childrenError !== null){
            string += this.childrenError + "\n";
        }
        if (this.children !== null){
            for (let childNode of this.children){
                string += childNode._branchToString(treeLevel+1);
            }
        }
        return string;
    }

    /** Converts the tree item to string
     */
    _nodeToString(){
        return `${this.name}  [${this.childrenState.toString()}]`;
    }

}

TreeItem.ChildrenState = {
    readyToLoad: Symbol("ready to load"),
    loading: Symbol("loading"),
    error: Symbol("error"),
    ready: Symbol("ready"),
}
Object.freeze(TreeItem.ChildrenState);