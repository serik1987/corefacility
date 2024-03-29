import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';
import ListLoader from 'corefacility-base/view/ListLoader';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import SlideDown from 'corefacility-base/shared-view/components/SlideDown';
import {ReactComponent as DropDown} from 'corefacility-base/shared-view/icons/dropdown_simple.svg';

import CoreWindowHeader from '../CoreWindowHeader';
import styles from './style.module.css';


/** Base class for all list loaders that  were displaced on the core page.
 * 	(Without any ability to be changed.)
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state options directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 * Basides,
 * 		@param {boolean} isFilterOpened true if the filter panel is in expanded state,
 * 						 false otherwise
 */
export default class CoreListLoader extends ListLoader{

	constructor(props){
		super(props);
		this.handleFilterChangeState = this.handleFilterChangeState.bind(this);

		this.state = {
			...this.state,
			isFilterOpened: false,
		}
	}

	/** The header to be displayed on the top.
	 */
	get listHeader(){
		throw new NotImplementedError("get listHeader");
	}

	/** Toggles the filter state between OPENED when filter widgets were
	 * 	displayed and CLOSED when they are not displayed.
	 * 
	 *  @param {SyntheticEvent} event the event that causes filter toggle.
	 * 		(e.g., Press on "Filter options" button).
	 */
	handleFilterChangeState(event){
		this.setState({isFilterOpened: !this.state.isFilterOpened});
	}

	/**	Renders the filter
	 * 	@return {React.Component} all filter widgets to be rendered
	 */
	renderFilter(){
		throw new NotImplementedError("renderFilter");
	}

	/** Renders the item list
	 * 	@return {React.Component} the rendered components
	 */
	renderItemList(){
		throw new NotImplementedError("renderItemList");
	}

	render(){
		let dropDownClassName = styles.filter_icon;
		if (this.state.isFilterOpened){
			dropDownClassName += ` ${styles.opened}`;
		}

		return (
			<CoreWindowHeader
				isLoading={this.isLoading}
				isError={this.isError}
				error={this.error}
				header={this.listHeader}
				aside={
					<PrimaryButton
						type="more"
						onClick={this.handleFilterChangeState}
						>
							{t("Filter options")}
							<DropDown
								className={dropDownClassName}
							/>
					</PrimaryButton>
				}
				>
					<div class={styles.wrapper}>
						<SlideDown isOpened={this.state.isFilterOpened} cssSuffix={` ${styles.filter_wrapper}`}>
							<div className={styles.filter}>
								{this.renderFilter()}
							</div>
						</SlideDown>
						<div className={styles.items_wrapper}>
							{this.renderItemList()}
						</div>
					</div>
			</CoreWindowHeader>
		);
	}

}