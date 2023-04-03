import {translate as t} from 'corefacility-base/utils';
import BaseApp from 'corefacility-base/view/App';
import User from 'corefacility-base/model/entity/User';
import Project from 'corefacility-base/model/entity/Project';

/** The root component in the imaging application
 *  
 *  Props (core application have no props, the other application contain information transmitted from the parent
 *      application to the child one using the props):
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {object}         translationResource             translation resources for the i18next translation module.
 *  @param {string}         token                           Authorization token received from the parent application.
 *                                                          undefined for the core application
 * 
 *  State (core application sets its state during the authorization process. Another applications receive part of
 *      their states from the parent's <ChildModuleFrame> component):
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {string}         token                           Authorization token received from the authorization
 *                                                          routines. null for any application except parent application
 */
export default class App extends BaseApp{

    /**
     *  Application name
     */
    static getApplicationName(){
        return 'imaging';
    }

    constructor(props){
        super(props);

        this.state = {
            ...this.state,
            user: null,
            project: null
        }
    }

    /**
     *  Returns the application user
     */
    get user(){
        return this.state.user;
    }

    /** Renders all routes.
     *  @abstract
     *  @return {React.Component} the component must be <Routes> from 'react-dom-routes'.
     */
    renderAllRoutes(){
        if (this.state.user !== null && this.state.project !== null){
            return <p>Success!</p>;
        } else {
            return <p>{t("Please wait while user and project info will be transmitted to the child frame.")}</p>;
        }
    }

}