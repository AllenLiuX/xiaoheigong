import React, { useState, useEffect } from "react";
import axios from 'axios';
import Loading from 'react-simple-loading';
import queryString from 'query-string';
import router from "next/router";
import Results from "./Results";

export default function Search() {
	const [inputText, setInputText] = useState("")
	const [inputDate, setInputDate] = useState("1")
	const [inputLength, setInputLength] = useState("10")
	const [inputType, setInputType] = useState("全部")
	const [articles, setArticles] = useState([])
	const [status, setStatus] = useState(Number())

	useEffect(() => {
		let url = window.location.search;
		let params = queryString.parse(url);
		setInputText(String(params["search_keyword"]))
		setInputDate(String(params["num_years"]))
		setInputLength(String(params["pdf_min_num_page"]))
		setInputType(String(params["inputType"]))
		console.log(params)
		fetchData(params)
	}, []);

	const submitHandler = event => {
		event.preventDefault();
		event.target.className += " was-validated";
		if (inputText != "") {
			const params = "search_keyword=" + inputText + "&num_years=" + inputDate + "&pdf_min_num_page=" + inputLength + "&inputType=" + inputType
			router.push("/search?" + params)
		}
	};

	const changeHandler = (input, fields) => {
		var params = ""
		var ret = {
			inputType: inputType,
			num_years: inputDate,
			pdf_min_num_page: inputLength,
			search_keyword: inputText
		}
		if (fields == 1) {
			setInputDate(input)
			params = "search_keyword=" + inputText + "&num_years=" + input + "&pdf_min_num_page=" + inputLength + "&inputType=" + inputType
			ret["num_years"] = input
			router.push("/search?" + params)

		}
		if (fields == 2) {
			setInputLength(input)
			params = "search_keyword=" + inputText + "&num_years=" + inputDate + "&pdf_min_num_page=" + input + "&inputType=" + inputType
			ret["pdf_min_num_page"] = input
		}
		if (fields == 3) {
			setInputType(input)
			params = "search_keyword=" + inputText + "&num_years=" + inputDate + "&pdf_min_num_page=" + inputLength + "&inputType=" + input
			ret["inputType"] = input

		}
		router.push("/search?" + params)
		fetchData(ret)
	};

	const fetchData = async (inp) => {
		const params = {
			search_keyword: String(inp["search_keyword"]),
			num_years: String(inp["num_years"]),
			pdf_min_num_page: String(inp["pdf_min_num_page"]),
			inputType: String(inp["inputType"])
		}
		JSON.stringify(params)
		/*axios.post(`http://8.210.91.108:5000/`, {params}) company, year, page, words */
		axios.post('http://localhost:5000', { params })
			.then(res => {
				console.log(res)
				setArticles(res.data.data.db_search_results)
			})
			.catch(err => {
				console.log(err);
				alert(err);
			});
	};

	return (
		<>
			<div className="row bg-bland-gray m-0">
				<div className="col-12">
					<div className="row pt-3 pb-3 bg-primary-darker">
						<div className="col-1">

						</div>
						<div className="col-3">
							<h4 className="align-middle m-1" style={{ color: "white" }}>
								小黑工企业信息服务平台
								</h4>
						</div>

						<div className="col-5">
							<form
								onSubmit={submitHandler}
							>
								<div className="row">
									<div className="col-8">
										<input
											type="text"
											className="form-control"
											placeholder={inputText}
											required
											value={inputText}
											onChange={(event) => setInputText(event.target.value)}

										></input>
									</div>

									<div className="col-4">
										<button type="submit" className="btn btn-primary btn-block">搜索</button>
									</div>
								</div>
							</form>
						</div>
					</div>
				</div>
			</div>
			<div className="row pt-4 bg-bland-gray m-0">
				<div className="col-12">
					<div className="row justify-content-center">

						<div className="col-2">
							<div className="row justify-content-center  bg-white rounded p-2">
								<div className="col-12">
									<div className="row justify-content-center">
										<div className="col-10">
											<div className="date-select">
												<label htmlFor="date-select" className="h5" > 日期</label>
												<hr />
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="1"
																id="year-1"
																checked={inputDate === "1"}
																onChange={(event) => changeHandler(event.target.value, 1)}
															/>
															<label className="custom-control-label" htmlFor="year-1">1年内</label>
														</div>
													</div>
												</div>
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="2"
																id="year-2"
																checked={inputDate === "2"}
																onChange={(event) => changeHandler(event.target.value, 1)}
															/>
															<label className="custom-control-label" htmlFor="year-2">2年内</label>
														</div>
													</div>
												</div>
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="3"
																id="year-3"
																checked={inputDate === "3"}
																onChange={(event) => changeHandler(event.target.value, 1)}
															/>
															<label className="custom-control-label" htmlFor="year-3"> 3年内</label>
														</div>
													</div>
												</div>
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="99"
																id="year-4"
																checked={inputDate === "99"}
																onChange={(event) => changeHandler(event.target.value, 1)}
															/>
															<label className="custom-control-label" htmlFor="year-4"> 不限</label>
														</div>
													</div>
												</div>
											</div>
										</div>
									</div>
									<hr />
									<div className="row justify-content-center">
										<div className="col-10">
											<div className="length-select">

												<label htmlFor="length-select" className="h5"> 页数</label>
												<hr />
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="10"
																id="length-1"
																checked={inputLength === "10"}
																onChange={(event) => changeHandler(event.target.value, 2)}
															/>
															<label className="custom-control-label" htmlFor="length-1">10页+</label>
														</div>
													</div>
												</div>
												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="20"
																id="length-2"
																checked={inputLength === "20"}
																onChange={(event) => changeHandler(event.target.value, 2)}
															/>
															<label className="custom-control-label" htmlFor="length-2">20页+</label>
														</div>
													</div>
												</div>

												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="30"
																id="length-3"
																checked={inputLength === "30"}
																onChange={(event) => changeHandler(event.target.value, 2)}
															/>
															<label className="custom-control-label" htmlFor="length-3">30页+</label>
														</div>
													</div>
												</div>

												<div className="row justify-content-center">
													<div className="col-12">
														<div className="custom-control custom-radio custom-control-inline">
															<input
																type="radio"
																className="custom-control-input"
																value="99"
																id="length-4"
																checked={inputLength === "99"}
																onChange={(event) => changeHandler(event.target.value, 2)}
															/>
															<label className="custom-control-label" htmlFor="length-4">不限</label>
														</div>
													</div>

												</div>
											</div>
										</div>
									</div>
									<hr />
									<div className="row justify-content-center">
										<div className="col-10">
											<div className="type-select">
												<label htmlFor="type-select" className="h5"> 资料种类: </label>
												<select className="custom-select custom-select-lg"
													onChange={(event) => changeHandler(event.target.value, 3)}
												>
													<option value="Default" selected>全部</option>
													<option value="NEWS">研报</option>
													<option value="REPORT">资讯</option>
												</select>
											</div>
										</div>
									</div>
								</div>
							</div>

						</div>
						<Results articles={articles} />

					</div>
				</div>
			</div>
		</>
	)
}
