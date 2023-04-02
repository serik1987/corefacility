import Module from 'corefacility-base/model/entity/Module';
import EntryPoint from 'corefacility-base/model/entity/EntryPoint';
import TreeItem from 'corefacility-base/model/tree/TreeItem';


/** Impelements an application tree and is used in the SettingsWindow
 *  component.
 */
export default class ModuleTreeItem extends TreeItem{

    RELOADING_CODES = [401, 403, 404]

    constructor(props){
        super(props);
        this.NodeType = this.constructor.NodeType;
    }

    /** Human-readable name of the tree item
     */
    get name(){
        return this.entity.name;
    }

    get nodeType(){
        if (this.entity instanceof Module){
            return this.NodeType.module;
        } else if (this.entity instanceof EntryPoint){
            return this.NodeType.entryPoint;
        } else {
            throw new Error("Bad entity class for the module tree item");
        }
    }

    _nodeToString(){
        return `[${this.nodeType}] ${super._nodeToString()}`;
    }

    /** Loads the children nodes from the external source. Please, note that children of the
     *  children are not children.
     */
    async loadChildren(){
        try{
            this._childrenState = this.ChildrenState.loading;
            this._childrenError = null;
            let childEntities = null;
            if (this.nodeType === this.NodeType.module){
                childEntities = await this.entity.findEntryPoints();
            } else {
                childEntities = await Module.find({entry_point: this.entity.id});
            }
            this._children = [...childEntities].map(entity => {
                let moduleTreeItem = new ModuleTreeItem(entity);
                moduleTreeItem.parent = this;
                return moduleTreeItem;
            });
            this._childrenState = this.ChildrenState.ready;
        } catch (error){
            if (this.RELOADING_CODES.indexOf(error.status) !== -1){
                window.location.reload();
            }
            this._childrenState = this.ChildrenState.error;
            this._childrenError = error.message;
        }
    }


}


ModuleTreeItem.NodeType = {
    module: "MD",
    entryPoint: "EP",
}
Object.freeze(ModuleTreeItem.NodeType);