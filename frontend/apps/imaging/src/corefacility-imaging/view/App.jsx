import {Routes, Route, Navigate} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import BaseApp from 'corefacility-base/view/App';
import User from 'corefacility-base/model/entity/User';
import NotificationMessage from 'corefacility-base/shared-view/components/NotificationMessage';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import Project from 'corefacility-imaging/model/entity/Project';

import DataSelector from './DataSelector';
import DataEditor from './DataEditor';
import DataCreateBox from './DataCreateBox';
import DataChangeBox from './DataChangeBox';
import RoiWrapper from './RoiWrapper';

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
        this.createFunctionalMap = this.createFunctionalMap.bind(this);
        this.changeFunctionalMap = this.changeFunctionalMap.bind(this);
        this.registerModal('add-data', DataCreateBox, {});
        this.registerModal('edit-data', DataChangeBox, {});

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

    /**
     *  Returns the application project
     */
    get project(){
        return this.state.project;
    }

    /**
     *  Receives entities from the parent applicatoin through the interframe communication (i.e., parent application
     *  runs this method to transmit its parent entities to this given application)
     *  @param {object} entityInfo  It depends on the specification of the parent application. Explore this object for
     *  more details
     */
    receiveParentEntities(entityInfo){
        this.setState({
            user: User.deserialize(entityInfo.user),
            project: Project.deserialize(entityInfo.project),
        });
    }

    /** 
     *  Renders all routes.
     *  @return {React.Component} the component must be <Routes> from 'react-dom-routes'.
     */
    renderAllRoutes(){
        if (this.state.user !== null && this.state.project !== null){
            return (
                <Routes>
                    <Route path="/data/:lookup/apps/roi/" element={
                        <DataSelector>
                            <RoiWrapper reloadTime={this.state.reloadTime}/>
                        </DataSelector>
                    }/>
                    <Route path="/data/:lookup/" element={
                        <DataSelector>
                            <DataEditor
                                reloadTime={this.state.reloadTime}
                                onItemAddOpen={this.createFunctionalMap}
                                onItemChangeOpen={this.changeFunctionalMap}
                            />
                        </DataSelector>
                    }/>
                    <Route path="/data/" element={
                        <DataEditor
                            reloadTime={this.state.reloadTime}
                            onItemAddOpen={this.createFunctionalMap}
                            onItemChangeOpen={this.changeFunctionalMap}
                        />
                    }/>
                    <Route path="/" element={<Navigate to="/data/"/>}/>
                    <Route path="*" element={
                        <NotificationMessage>
                            {t("The requested page was not found.")}
                            {' '}
                            <Hyperlink href="/">{t("Switch to the Main Page.")}</Hyperlink>
                        </NotificationMessage>}
                    />
                </Routes>
            );
        } else {
            return (
                <NotificationMessage>
                    {t("Please wait while user and project info will be transmitted to the child frame.")}
                </NotificationMessage>
            );
        }
    }

    /**
     *  Triggers when the user tries to add new functional map.
     *  @param {SyntheticEvent} the event that triggered this action
     *  @return {FunctionalMap|boolean} created functional map or false in case of failure.
     */
    async createFunctionalMap(event){
        return await this.openModal('add-data', {});
    }

    /**
     *  Triggers when the user tries to remove functional map.
     *  @param {FunctionalMap}  functionalMap       the functional map before change
     *  @return {FunctionalMap}                     the functional map after change
     */
    async changeFunctionalMap(functionalMap){
        return await this.openModal('edit-data', {
            lookup: [window.application.project.id, functionalMap.id]
        });
    }

}