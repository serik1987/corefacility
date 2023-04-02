import {translate as t} from 'corefacility-base/utils';
import ModuleWidget from 'corefacility-base/model/ModuleWidget';
import Loader from 'corefacility-base/view/Loader';
import style from './style.module.css';


/** Draws widgets for all modules belonging to a given entry point
 * 
 * Props:
 * ---------------------------------------------------------------------------------------------------------------------
 * @param {string} parentModuleUuid				UUID of a module that has a given entry point
 * @param {string} entryPointAlias				alias of this given entry point
 * @param {callback} onClick					This method will be invoked when the user clicks a module widget
 * 												The only argument is ModuleWidget object that represents a certain
 * 												widget that has been clicked
 * @param {boolean} inactive					The user can't select a given module by clicking on the module widget
 * @param {string} cssSuffix 					Additional CSS classes to apply
 * @param {callback} onWidgetsEmpty 			Triggers when the list of widgets contain no widgets
 * ---------------------------------------------------------------------------------------------------------------------
 */
export default class ModuleWidgets extends Loader{

	constructor(props){
		super(props);
		this.setContainerRef = this.setContainerRef.bind(this);
		this.onClick = this.onClick.bind(this);
		this.tryAgain = this.tryAgain.bind(this);

		this.state = {
			moduleWidgets: [],
			isLoading: false,
			isError: false
		}

		this.__widgetContainer = null;
	}

	setContainerRef(element){
		this.__widgetContainer = element;
	}

	onClick(event){
		event.preventDefault();
		if (this.props.inactive){
			return;
		}
		let dataset = event.target.closest(`.${style.widget_wrapper}`).dataset;
		let widget = new ModuleWidget(dataset.uuid, dataset.alias, dataset.name, null);
		if (this.props.onClick){
			this.props.onClick(widget);
		}
	}

	tryAgain(event){
		if (this.props.inactive){
			return;
		}
		this.reload();
	}

	/** Reloads the data. This method runs automatically when the componentDidMount.
	 * 	Also, you can invoke it using the imperative React principle
	 * 	@async
	 * 	@return {undefined}
	 */
	async reload(){
		try{
			this.setState({
				moduleWidgets: null,
				isLoading: true,
				isError: false
			});
			let newWidgets = [];
			for await (let widget of ModuleWidget.find(this.props.parentModuleUuid, this.props.entryPointAlias)){
				newWidgets.push(widget);
			}
			this.setState({
				moduleWidgets: newWidgets,
				isLoading: false,
				isError: false,
			});
			newWidgets = newWidgets.filter(widget => widget.htmlCode);
			if (newWidgets.length === 0 && this.props.onWidgetsEmpty){
				this.props.onWidgetsEmpty();
			}
		} catch (error){
			this.setState({
				moduleWidgets: null,
				isLoading: false,
				isError: true,
			});
		}
	}

	shouldComponentUpdate(nextProps, nextState){
		return this.state.moduleWidgets !== nextState.moduleWidgets ||
			this.state.isLoading !== nextState.isLoading ||
			this.state.isError !== nextState.isError ||
			this.props.inactive !== nextProps.inactive ||
			this.props.cssSuffix !== nextProps.cssSuffix;
	}

	render(){
		let css = `${style.widgets}`;
		if (this.props.inactive){
			css += ` ${style.inactive}`;
		}
		if (this.props.cssSuffix){
			css += ` ${this.props.cssSuffix}`;
		}

		return (
			<div className={css}>
				{this.state.moduleWidgets && this.state.moduleWidgets.length !== 0 &&
					<div className={style.container} ref={this.setContainerRef}></div>}
				{this.state.isLoading && <p>{t("Loading...")}</p>}
				{this.state.isError &&
					<p className={style.error}>
						{t("Unable to load authorization methods.")}{' '}
						<a href="#" onClick={this.tryAgain}>{t("Try again.")}</a>
					</p>}
			</div>
		)
	}

	componentDidUpdate(prevProps, prevState){
		if (this.__widgetContainer === null){
			return;
		}
		this.__widgetContainer.innerHTML = '';

		for (let moduleWidget of this.state.moduleWidgets){
			if (!moduleWidget.htmlCode){
				continue;
			}

			let widgetWrapper = document.createElement('div');
			widgetWrapper.innerHTML = moduleWidget.htmlCode;
			widgetWrapper.classList.add(style.widget_wrapper);
			widgetWrapper.dataset.uuid = moduleWidget.uuid;
			widgetWrapper.dataset.alias = moduleWidget.alias;
			widgetWrapper.dataset.name = moduleWidget.name;
			widgetWrapper.title = moduleWidget.name;
			widgetWrapper.addEventListener('click', this.onClick);
			this.__widgetContainer.append(widgetWrapper);
		}
	}

}
