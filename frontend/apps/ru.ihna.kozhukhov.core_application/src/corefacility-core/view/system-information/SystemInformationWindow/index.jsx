import * as React from 'react';

import {translate as t, humanReadableMemory} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import {UnauthorizedError} from 'corefacility-base/exceptions/network';
import Sidebar from 'corefacility-base/shared-view/components/Sidebar';
import SidebarItem from 'corefacility-base/shared-view/components/SidebarItem';
import PieChart from 'corefacility-base/shared-view/components/PieChart';
import BarChart from 'corefacility-base/shared-view/components/BarChart';
import Table from 'corefacility-base/shared-view/components/Table';
import {ReactComponent as MonitoringIcon} from 'corefacility-base/shared-view/icons/monitoring.svg';
import {ReactComponent as DevicesIcon} from 'corefacility-base/shared-view/icons/devices.svg';

import CoreWindow from '../../base/CoreWindow';
import CoreWindowHeader from '../../base/CoreWindowHeader';
import style from './style.module.css';


/**
 * 	Represents a window that short information about the Web server
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	@param {String} 	mode 			'current_statistics' if current statistics is displayed,
 * 										'system_information' if system information is displayed
 * 	@param {boolean} 	isLoading 		true is parameter information is loading, false otherwise
 * 	@param {string} 	error 			Error message to display or null if this is not required.
 * 
 * 	Another state parameters should be modified by the reload() method (don't do this alone!).
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class SystemInformationWindow extends CoreWindow{

	/* Contants that control the system information reveal */
	URL = `/api/${window.SETTINGS.client_version}/sysinfo/`;
	SEC_IN_MINUTE = 60
	SEC_IN_HOUR = 3600
	SEC_IN_DAY = 86400

	/* Constants that control the system information visualization */
	PRECISION = 2;
	LOAD_AVERAGE_COLORS = ["rgb(242, 140, 40)", "rgba(242, 140, 40, 0.25)"];
	MEMORY_INFO_COLORS =
			["rgb(136, 8, 8)", "rgba(136, 8, 8, 0.25)", "rgba(34, 139, 34, 0.25)", "rgb(34, 139, 34)"];
	DISK_SPACE_TEXT_COLOR = "rgb(136, 8, 8)";
	REFRESH_INTERVAL = 15000;

	constructor(props){
		super(props);
		this.__chartRef = React.createRef();
		this.__firstResize = false;

		this.PHYSICAL_MEMORY_AVAILABLE_COLOR = this.MEMORY_INFO_COLORS[1];
		this.PHYSICAL_MEMORY_COLORS = this.MEMORY_INFO_COLORS.slice(0, 2).reverse();
		this.SWAP_AVAILABLE_COLOR = this.MEMORY_INFO_COLORS[2];
		this.SWAP_COLORS = this.MEMORY_INFO_COLORS.slice(2);

		this.state = {
			...this.state,
			mode: 'current_statistics',
			isLoading: false,
			error: null,

			uptime: t("undefined"),
			loadAverage: 0,
			cpuCores: 0,
			memoryAvailablePerc: 0,
			swapAvailablePerc: 0,
			memoryInfoReceived: false,
			memoryAvailable: 0,
			memoryTotal: 0,
			swapAvailable: 0,
			swapTotal: 0,
			diskUsage: null,
			diskSpaceInfo: null,
			diskTotal: null,
			networkInfo: null,
			hostname: null,
			osInfo: null,

			_noRepaint: false,
			_temporaryInvisible: false,
		}

		this.__timeout = null;
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("System information")
	}

	get chartContainer(){
		return this.__chartRef.current;
	}

	/**
	 *  Downloads and reformats the system information
	 */
	async reload(){
		if (this.__timeout){
			clearTimeout(this.__timeout);
			this.__timeout = null;
		}
		try{
			this.setState({error: null, _noRepaint: true});
			let result = await client.get(this.URL);
			this.__setUptime(result.uptime);
			this.__setCpuInfo(result.cpu_info);
			this.__setMemoryInfo(result.memory_info, result.swap_info);
			this.__setDiskUsage(result.disk_info);
			this.__setNetworkInfo(result.network_info);
			this.__setOsInfo(result.os_info);
		} catch (error){
			this.setState({error: error.message});
			if (error instanceof UnauthorizedError){
				window.location.reload();
			}
		} finally{
			this.setState({_noRepaint: false});
			this.__timeout = setTimeout(() => this.reload(), this.REFRESH_INTERVAL);
		}
	}

	/**
	 * 	Changes sizes of all charts when the size of the "parent chart" modifies.
	 */
	resizeCharts(){
		if (this.__firstResize){
			this.__firstResize = false;
		} else {
			this.setState({_temporaryInvisible: true});
		}
	}

	/** Renders the area on the top of the Web browser window;
	 *  between the logo and the controls
	 * 	@return {React.js component}
	 */
	renderControls(){
		return null;
	}

	/** Renders the rest part of the window; below the window header
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		let loadAverageData = null;
		if (this.state.loadAverage < this.state.cpuCores){
			loadAverageData = [this.state.loadAverage, this.state.cpuCores - this.state.loadAverage];
		} else {
			loadAverageData = [this.state.cpuCores, this.state.cpuCores];
		}

		let memoryUsed, swapUsed;
		let memoryAvailable = this.state.memoryAvailablePerc;
		let swapAvailable = this.state.swapAvailablePerc;
		if (this.state.memoryInfoReceived){
			memoryUsed = 1 - memoryAvailable;
			swapUsed = 1 - swapAvailable;
		} else {
			memoryUsed = 0;
			swapUsed = 0;
		}
		let memoryInfoData = [memoryUsed, memoryAvailable, swapAvailable, swapUsed];

		let chartCommonProps = {
			noRepaint: this.state._noRepaint,
			followResize: false,
			visible: !this.state._temporaryInvisible,
		}

		return (
			<CoreWindowHeader
				isLoading={this.state.isLoading}
				isError={this.state.error !== null}
				error={this.state.error}
				header={t("System information")}
				cssSuffix={style.window_header}
			>
				<Sidebar
					items={[
						<SidebarItem
							current={this.state.mode === 'current_statistics'}
							text={t("Current statistics")}
							onClick={event => this.handleSidebarSelection('current_statistics')}
							tooltip={t("Displays uptime, CPU, memory, disk and network usage")}
							icon={<MonitoringIcon/>}
						/>,
						<SidebarItem
							current={this.state.mode === 'system_information'}
							text={t("System information")}
							onClick={event => this.handleSidebarSelection('system_information')}
							tooltip={t("Displays general information about installed hardware and software")}
							icon={<DevicesIcon/>}
						/>
					]}
				>
					{this.state.mode === 'current_statistics' &&
					<div className={`${style.panel} ${style.current_statistics_panel}`} ref={this.__chartRef}>
						<section className={style.uptime_section}>
							<h2>{t("Uptime")}: {this.state.uptime}</h2>
						</section>
						<section className={style.cpu_section}>
							<h2>{t("CPU usage")}</h2>
							<PieChart
								data={loadAverageData}
								colors={this.LOAD_AVERAGE_COLORS}
								bagelInnerRadius={0.7}
								{...chartCommonProps}
							/>
							<div className={style.pie_chart_legend}>
								{this.renderPieChartLabel(
									this.LOAD_AVERAGE_COLORS[0],
									t("CPU load average"),
									this.state.loadAverage.toFixed(this.PRECISION),
									t("CPU_LOAD_AVERAGE_DESCRIPTION")
								)}
								{this.renderPieChartLabel(
									this.LOAD_AVERAGE_COLORS,
									t("Total number of cores"),
									this.state.cpuCores
								)}
							</div>
						</section>
						<section className={style.memory_section}>
							<h2>{t("Memory usage")}</h2>
							<PieChart
								data={memoryInfoData}
								colors={this.MEMORY_INFO_COLORS}
								bagelInnerRadius={0.7}
								{...chartCommonProps}
							/>
							<div className={style.pie_chart_legend_group}>
								<div className={style.pie_chart_legend}>
									{this.renderPieChartLabel(
										this.PHYSICAL_MEMORY_AVAILABLE_COLOR,
										t("Available physical memory"),
										this.state.memoryAvailable,
										t("AVAILABLE_PHYSICAL_MEMORY_DESCRIPTION")
									)}
									{this.renderPieChartLabel(
										this.PHYSICAL_MEMORY_COLORS,
										t("Total physical memory"),
										this.state.memoryTotal,
									)}
								</div>
								<div className={style.pie_chart_legend}>
									{this.renderPieChartLabel(
										this.SWAP_AVAILABLE_COLOR,
										t("Available swap memory"),
										this.state.swapAvailable,
										t("AVAILABLE_SWAP_MEMORY_DESCRIPTION")
									)}
									{this.renderPieChartLabel(
										this.SWAP_COLORS,
										t("Total swap memory"),
										this.state.swapTotal,
									)}
								</div>
							</div>
						</section>
						<section className={style.disk_section}>
							<h2>{t("Disk usage")}</h2>

							{this.state.diskUsage && Object.keys(this.state.diskUsage).length > 0 && 
								<BarChart
									data={this.state.diskUsage}
									labeledText={this.state.diskSpaceInfo}
									labeledTextColor={this.DISK_SPACE_TEXT_COLOR}
									{...chartCommonProps}
								/>
							}
							{this.state.diskUsage && Object.keys(this.state.diskUsage).length === 0 && 
								<p><i>{t("No disks were found in /etc/fstab")}</i></p>
							}
						</section>
						<section className={style.network_section}>
							<h2>{t("Network usage")}</h2>
							{this.state.networkInfo &&
								<Table
									columns={[
										t("Received"),
										t("Sent"),
									]}
									rows={[
										t("Amount of information"),
										t("Number of packets"),
										t("Number of errors"),
										t("Number of drops"),
									]}
									data={this.state.networkInfo}
								/>
							}
						</section>
					</div>}
					{this.state.mode === 'system_information' &&
					<div className={style.panel}>
						<dl className={style.sysinfo}>
							<dt>{t("Hostname")}</dt>
							<dd>{this.state.hostname}</dd>
							<dt>{t("CPU")}</dt>
							<dd>{`${this.state.cpuName} \u00d7 ${this.state.cpuCores}`}</dd>
							<dt>{t("Operating memory")}</dt>
							<dd>{this.state.memoryTotal}</dd>
							<dt>
								{t("Hard disks volume")}
								<small>{t("Only those mentioned in /etc/fstab are considered")}</small>
							</dt>
							<dd>{this.state.diskTotal}</dd>
						</dl>
						<dl className={style.sysinfo}>
							<dt>{t("Is POSIX compatible")}</dt>
							<dd>{this.state.osInfo.posix}</dd>
							<dt>{t("Platform")}</dt>
							<dd>{this.state.osInfo.platform}</dd>
							<dt>{t("Kernel version")}</dt>
							<dd>{this.state.osInfo.kernelVersion}</dd>
							<dt>{t("Operating system name")}</dt>
							<dd>{this.state.osInfo.name}</dd>
							<dt>{t("Operating system type")}</dt>
							<dd>{this.state.osInfo.architecture}</dd>
						</dl>
					</div>}
				</Sidebar>
			</CoreWindowHeader>
		);
	}

	/**
	 * 	Renders a single label located at the bottom of pie charts.
	 * 
	 * 	@param {Array|String} 	colors 		CSS values for the labeled colors
	 * 	@param {String} 		text 		A short text that will be located at the right of the labeled colors
	 * 	@param {String} 		value 		Value of the magnitude shown on the pie chart. String is preferrable,
	 * 										another values will be converted to strings automatically according to
	 * 										Javascript convertion rules
	 * 	@param {String} 		title 		Long description of the magnitude that will be shown to the user in the form
	 * 										of tooltip
	 */
	renderPieChartLabel(colors, text, value, title=undefined){
		if (!(colors instanceof Array)){
			colors = [colors];
		}

		return (
			<div className={style.pie_chart_label}>
				{colors.map(color => {
					return (
						<span
							className={style.pie_chart_graphic_label}
							style={{backgroundColor: color}}
						></span>
					);
				})}
				<span
					className={style.pie_chart_text_label}
					title={title}
				>
					{text}
					{": "}
					<strong>{value}</strong>
				</span>
			</div>
		);
	}

	componentDidMount(){
		this.__firstResize = true;
		this.__resizeObserver = new ResizeObserver(entry => this.resizeCharts());
		this.__resizeObserver.observe(this.chartContainer);

		this.reload();
	}

	componentDidUpdate(prevProps, prevState){
		if (this.state._temporaryInvisible){
			this.setState({_temporaryInvisible: false});
		}
	}

	componentWillUnmount(){
		this.__resizeObserver.disconnect(this.chartContainer);

		if (this.__timeout !== null){
			clearTimeout(this.__timeout);
		}
	}

	/**
	 * 	Triggers when the user selects an items from the left menu.
	 * 
	 * 	@param {string}  option 		Desired state of this React component.
	 */
	handleSidebarSelection(option){
		this.setState({mode: option});
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		this.setState({isLoading: true});
		await this.reload();
		this.setState({isLoading: false});
	}

	/**
	 * 	Updates the state in such a way as the user can see the uptime
	 * 
	 * 	@param {Number} uptime  total number of seconds elapsed since the current system boot
	 */
	__setUptime(uptime){
		let remaining_uptime = uptime;		
		let days = Math.floor(uptime / this.SEC_IN_DAY);
		remaining_uptime = uptime - days * this.SEC_IN_DAY;
		let hours = Math.floor(remaining_uptime / this.SEC_IN_HOUR);
		remaining_uptime -= hours * this.SEC_IN_HOUR;
		let minutes = Math.floor(remaining_uptime / this.SEC_IN_MINUTE);
		remaining_uptime -= minutes * this.SEC_IN_MINUTE;
		let seconds = Math.round(remaining_uptime);

		let uptimeString = [];
		if (days > 0){
			uptimeString.push(days + " " + t("days"));
		}
		if (hours > 0){
			uptimeString.push(hours + " " + t("hours"));
		}
		if (minutes > 0){
			uptimeString.push(minutes + " " + t("minutes"));
		}
		if (seconds > 0){
			uptimeString.push(seconds + " " + t("seconds"));
		}
		uptimeString = uptimeString.join(" ");

		this.setState({uptime: uptimeString});
	}

	/**
	 * 	Updates the state in such a way as the user can see the CPU information
	 * 
	 * 	@param {Object} cpuInfo  the 'cpu_info' field received from the Web server
	 */
	__setCpuInfo(cpuInfo){
		let loadAverage = 0;
		if (cpuInfo.load_average.length > 0){
			loadAverage = cpuInfo.load_average[0];
		}

		this.setState({
			loadAverage: loadAverage,
			cpuName: cpuInfo.name,
			cpuCores: cpuInfo.cores,
		});
	}

	/**
	 * 	Updates the state in such a way as the user can see the memory information
	 * 
	 * 	@param {Object} memoryInfo information about available and total physical memory
	 * 	@param {Object} swapInfo information about available and total swap memory
	 */
	__setMemoryInfo(memoryInfo, swapInfo){
		this.setState({
			memoryAvailablePerc: memoryInfo.available / memoryInfo.total,
			swapAvailablePerc: swapInfo.available / swapInfo.total,
			memoryInfoReceived: true,
			memoryAvailable: humanReadableMemory(memoryInfo.available),
			memoryTotal: humanReadableMemory(memoryInfo.total),
			swapAvailable: humanReadableMemory(swapInfo.available),
			swapTotal: humanReadableMemory(swapInfo.total),
		})
	}

	/**
	 * 	Updates the state in such a way as it contains the disk usage
	 * 
	 * 	@param {Object} diskInfo  information about available disk usage.
	 */
	__setDiskUsage(diskInfo){
		let diskUsage = {};
		let diskSpaceInfo = {};
		let diskTotal = 0;
		for (let mountPoint in diskInfo){
			let diskSpaces = diskInfo[mountPoint];
			diskUsage[mountPoint] = [
				(diskSpaces.total - diskSpaces.available) / diskSpaces.total,
				diskSpaces.available / diskSpaces.total,
			];
			let diskSpaceFree = humanReadableMemory(diskSpaces.available);
			let diskSpaceTotal = humanReadableMemory(diskSpaces.total);
			diskSpaceInfo[mountPoint] = `${t("Free")}: ${diskSpaceFree} / ${diskSpaceTotal}`;
			diskTotal += diskSpaceTotal;
		}
		this.setState({
			diskUsage: diskUsage,
			diskSpaceInfo: diskSpaceInfo,
			diskTotal: humanReadableMemory(diskTotal),
		});
	}

	/**
	 * 	Updates the component state in such a way as it contains the network information
	 * 
	 * 	@param {Object} networkInfo 	an information about the network state received from the Web server
	 */
	__setNetworkInfo(networkInfo){
		this.setState({networkInfo: [
			[	humanReadableMemory(networkInfo.bytes_received), 	humanReadableMemory(networkInfo.bytes_sent),	],
			[	networkInfo.packets_received,						networkInfo.packets_sent,						],
			[	networkInfo.errors_input,							networkInfo.errors_output,						],
			[	networkInfo.drops_input,							networkInfo.drops_output,						],
		]});
		this.setState({hostname: networkInfo.hostname});
	}

	/**
	 * 	Updates the OS info according to the information received from the sever
	 * 
	 * 	@param {Object} osInfo 		value of the 'os_info' field from the server response
	 */
	__setOsInfo(osInfo){
		this.setState({
			osInfo: {
				name: osInfo.os_version,
				architecture: osInfo.architecture,
				platform: osInfo.platform,
				kernelVersion: osInfo.kernel_version,
				posix: osInfo.posix ? t("Yes") : t("No"),
			}
		});
	}


}