import {Routes, Route, Navigate} from 'react-router-dom';

import User from 'corefacility-base/model/entity/User';
import Project from 'corefacility-base/model/entity/Project';
import BaseApp from 'corefacility-base/view/App';
import FunctionalMap from 'corefacility-roi/model/FunctionalMap';

import style from './style.module.css';
import RectangularRoiEditor from '../RectangularRoiEditor';
import RectangularRoiForm from '../RectangularRoiForm';
import PinwheelEditor from '../PinwheelEditor';
import PinwheelForm from '../PinwheelForm';


/** Base class for application root components
 *  
 * 	Props (core application have no props, the other application contain information transmitted from the parent
 * 		application to the child one using the props):
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {object} 		translationResource 			translation resources for the i18next translation module.
 * 	@param {string}			token 							Authorization token received from the parent application.
 * 															undefined for the core application
 * 
 * 	State (core application sets its state during the authorization process. Another applications receive part of
 * 		their states from the parent's <ChildModuleFrame> component):
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 		token 							Authorization token received from the authorization
 * 															routines. null for any application except parent application
 * 	@param {string} 		reloadTime 						Timestamp of the last reload. This is required for the
 * 															interframe communication.
 */
export default class App extends BaseApp{

    constructor(props){
        super(props);
        this.registerModal('edit-rectangular-roi', RectangularRoiForm);
        this.registerModal('edit-pinwheel', PinwheelForm);

        this.state = {
            ...this.state,
            project: null,
            functionalMap: null,
        }
    }

    /**
     *  Returns the current project.
     */
    get project(){
        return this.state.project;
    }

    /**
     *  Returns the functional map.
     */
    get functionalMap(){
        return this.state.functionalMap;
    }

	/**
	 * 	Application name
	 */
	static getApplicationName(){
		return 'roi'
	}

    /**
     *  Receives entities from the parent applicatoin through the interframe communication (i.e., parent application
     *  runs this method to transmit its parent entities to this given application)
     *  @param {object} entityInfo  It depends on the specification of the parent application. Explore this object for
     *  more details
     */
    receiveParentEntities(entityInfo){
        this.user = User.deserialize(entityInfo.user_info);
        this.setState({
            project: Project.deserialize(entityInfo.project_info),
            functionalMap: FunctionalMap.deserialize(entityInfo.functional_map_info),
        });
        this.reload();
    }

	/** Renders all routes.
	 * 	@return {React.Component} the component must be <Routes> from 'react-dom-routes'.
	 */
	renderAllRoutes(){
		return (
            <Routes>
                <Route path="/rectangular/" element={<RectangularRoiEditor reloadTime={this.state.reloadTime}/>}/>
                <Route path="/pinwheels/" element={<PinwheelEditor reloadTime={this.state.reloadTime}/>}/>
                <Route path="*" element={<Navigate to="/rectangular/"/>}/>
            </Routes>
        );
	}

}