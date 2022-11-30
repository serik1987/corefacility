import EntityInputList from 'corefacility-base/view/EntityInputList';

import styles from './style.module.css';


/** Provides special user list for the UserInput component
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
export default class UserInputList extends EntityInputList{

    handleItemSelect(user){
        if (this.props.onItemSelect){
            this.props.onItemSelect(user);
        }
    }

    /** Renders content where single item will be shown
     *  @param {User} user the user to be rendered
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(user){
        let name = "";
        let title = "";
        if (user.surname && user.name){
            name = `${user.surname} ${user.name}`;
            title = name;
        } else {
            name = null;
            title = user.login;
        }

        return (
            <li
                key={user.id}
                data-id={user.id}
                onClick={this.onItemSelect}
                className={styles.item_container}
                onClick={event => this.handleItemSelect(user)}
                >
                    <div className={styles.image_box}>
                        <img src={user.avatar} alt={user.avatar}/>
                    </div>
                    <div className={styles.data_box}>
                        <div className={styles.title_box}>{title}</div>
                        {name !== null && <div className={styles.login_box}>{user.login}</div>}
                    </div>
            </li>
        );
    }

}