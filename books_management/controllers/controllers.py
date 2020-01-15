# -*- coding: utf-8 -*-
from openerp import http

# class BooksManagement(http.Controller):
#     @http.route('/books_management/books_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/books_management/books_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('books_management.listing', {
#             'root': '/books_management/books_management',
#             'objects': http.request.env['books_management.books_management'].search([]),
#         })

#     @http.route('/books_management/books_management/objects/<model("books_management.books_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('books_management.object', {
#             'object': obj
#         })