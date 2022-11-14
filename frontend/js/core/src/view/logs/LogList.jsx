import {translate as t} from '../../utils.mjs';

import PaginatedList from '../base/PaginatedList.jsx';
import ImagedListItem from '../base/ImagedListItem.jsx';
import {ReactComponent as ViewIcon} from '../base-svg/visibility.svg';
import {ReactComponent as AddIcon} from '../base-svg/add.svg';
import {ReactComponent as EditIcon} from '../base-svg/edit.svg';
import {ReactComponent as RemoveIcon} from '../base-svg/delete.svg';
import styles from './LogList.module.css';

const STATUS = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad request's input data",
    401: "Not Authorized",
    403: "Permission denied",
    404: "Not found",
    405: "Method not allowed",
    406: "Not acceptable",
    429: "Maximum request number exceeded",
    500: "Internal server error",
}


/** Defines the widget that allows to reveal given logs
 * 
 * 	Props:
 * 		@param {EntityPage|null} items 		The item list, as it passed by the parent component.
 * 											Must be an instance of EntityPage
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload the list.
 * 		@param {callback} onItemSelect		The function calls when the user clicks on a single item in the list (optional)
 * 
 * 	State:
 * 		@param {Array of Entity} items 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class LogList extends PaginatedList{

    /** Renders one single log
     *  @param {Log} log to be render
     *  @return {Rect.Component} the component to render. The component must be a single
     *          item with the following conditions met:
     *              - the component must be an instance of the ListItem
     *              - its root element must be <li>
     *              - its key prop must be equal to item.id
     *              - its onClick prop must be equal to this.props.onItemSelect
     */
    renderItemContent(log){
        let avatar = "/static/core/user.svg"
        if (log.user){
            avatar = log.user.avatar;
        }

        let user_description = null;
        if (log.user === null){
            user_description = t("anonymous");
        } else if (log.user.name === null || log.user.surname === null){
            user_description = log.user.login;
        } else {
            user_description = `${log.user.surname} ${log.user.name}`;
        }

        let statusCss = null;
        let statusMsg = t("Response status");
        if (200 <= log.response_status && log.response_status < 400){
            statusCss = styles.success;
        } else if (!log.response_status){
            statusCss = null;
        } else {
            statusCss = styles.failure;
            statusMsg = t("Error")
        }

        let MethodIcon = null;
        switch (log.request_method){
            case "GET":
                MethodIcon = ViewIcon;
                break;
            case "POST":
                MethodIcon = AddIcon;
                break;
            case "PATCH":
            case "PUT":
                MethodIcon = EditIcon;
                break;
            case "DELETE":
                MethodIcon = RemoveIcon;
        }

        let methodIcon = null;
        let statusLine = null;
        if (MethodIcon !== null){
            methodIcon = <MethodIcon className={statusCss}/>;
            if (statusCss === styles.failure){
                statusLine = <div className={styles.cross_fail}></div>;
            }
            if (statusCss === styles.failure && MethodIcon === EditIcon){
                statusLine = <div className={[styles.cross_fail, styles.reverse].join(' ')}></div>;
            }
        }

        let responseStatus = t("undefined");
        if (log.response_status){
            responseStatus = `${log.response_status} ${log.response_status in STATUS ? t(STATUS[log.response_status]) : ''}`;
        }

        return (
            <ImagedListItem
                key={log.id}
                inactive={this.isLoading}
                href={`/logs/${log.id}/`}
                item={log}
                img={avatar}
                imageWidth={75}
                imageHeight={75}
                >
                    <div class={styles.section_container}>
                        <div class={styles.section}>
                            <h2>{log.request_date.toLocaleDateString()}</h2>
                            <small>{log.request_date.toLocaleTimeString()}</small>
                            <small>IP: {log.ip_address}</small>
                        </div>
                        <div class={styles.section}>
                            <h2>
                                {methodIcon}{statusLine}
                                <span className={styles.section_header}>{t(log.operation_description)}
                            </span>
                            </h2>
                            <small>{t("User")}: {user_description}</small>
                            <small>{t("Request method")}: {log.request_method}</small>
                            <small className={statusCss}>{statusMsg}: {responseStatus}</small>
                        </div>
                    </div>
            </ImagedListItem>
        );
    }

    render(){
        if (this.state.itemArray.length === 0 && !this.isLoading){
            return <p className={styles.no_logs}>{t("There are no requests satisfying given filter conditions.")}</p>;
        }
        return super.render();
    }

}