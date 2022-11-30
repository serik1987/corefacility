import ItemList from './ItemList.jsx';


/** Base class for all lists that deliver items to the user box
 * 
 * 	Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *      @param {iterable|null} items        The item list, as it passed by the parent component.
 *                                          Can be any iterable component. However, subtypes may require instance
 *                                          of a certain class
 * 
 *      @param {boolean} isLoading          true if the parent component is in 'loading' state.
 * 
 *      @param {boolean} isError            true if the parent component is failed to reload this item list.
 * 
 *      @param {callback} onItemSelect      The function calls when the user clicks on a single item in the list
 *                                          (optional)
 *  --------------------------------------------------------------------------------------------------------------------
 * 
 *  State:
 *  --------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class EntityInputList extends ItemList{

    constructor(props){
        super(props);
        this.handleItemSelect = this.handleItemSelect.bind(this);
    }

    /** Handles selection of a given item. To cause your widget working properly you have to asssign this function to
     *  onClick callback of the item container.
     * 
     *  @param {SyntheticEvent} event the event that has been triggered this callback
     *  @return {undefined}
     */
    handleItemSelect(event){
        let entityId = event.target.closest("li").dataset.id;
        if (this.props.onItemSelect){
            this.props.onItemSelect({...event, value: entityId});
        }
    }

    render(){
        return this.renderContent();
    }

}